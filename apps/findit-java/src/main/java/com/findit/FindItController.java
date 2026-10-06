package com.findit;

import com.findit.ApiModels.DashboardSummary;
import com.findit.ApiModels.ErrorResponse;
import com.findit.ApiModels.HealthStatus;
import com.findit.ApiModels.Item;
import com.findit.ApiModels.Match;
import com.findit.ApiModels.Message;
import com.findit.ApiModels.MessageInput;
import com.findit.ApiModels.ReportInput;
import com.findit.ApiModels.ReturnConfirmationInput;
import com.findit.ApiModels.VerificationInput;
import com.findit.ApiModels.VerificationResult;
import java.net.URI;
import java.time.Instant;
import java.time.LocalDate;
import java.util.List;
import java.util.Locale;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.server.ResponseStatusException;

@RestController
public class FindItController {
  private static final int MAX_NAME_LENGTH = 100;
  private final JdbcTemplate jdbc;
  private final ItemRepository items;
  private final MatchRepository matches;
  private final MatchingService matching;
  private final MessageRepository messages;

  public FindItController(
      JdbcTemplate jdbc,
      ItemRepository items,
      MatchRepository matches,
      MatchingService matching,
      MessageRepository messages
  ) {
    this.jdbc = jdbc;
    this.items = items;
    this.matches = matches;
    this.matching = matching;
    this.messages = messages;
  }

  @GetMapping("/healthz")
  public HealthStatus health() {
    return new HealthStatus("healthy");
  }

  @GetMapping("/dashboard")
  public DashboardSummary dashboard() {
    int total = count("SELECT COUNT(*) FROM findit_items");
    int lost = count("SELECT COUNT(*) FROM findit_items WHERE type = 'LOST'");
    int found = count("SELECT COUNT(*) FROM findit_items WHERE type = 'FOUND'");
    int open = count("SELECT COUNT(*) FROM findit_items WHERE status = 'OPEN'");
    int potential = count("""
        SELECT COUNT(*) FROM findit_matches
        WHERE verified = FALSE AND lost_confirmed = FALSE AND found_confirmed = FALSE
        """);
    int returned = count("""
        SELECT COUNT(*) FROM findit_matches
        WHERE lost_confirmed = TRUE AND found_confirmed = TRUE
        """);
    return new DashboardSummary(total, lost, found, open, potential, returned);
  }

  @GetMapping("/items")
  public List<Item> getItems(
      @RequestParam(required = false) String type,
      @RequestParam(required = false, name = "q") String search,
      @RequestParam(required = false) String status
  ) {
    return items.list(type, search, status);
  }

  @PostMapping("/items")
  public ResponseEntity<Item> createItem(@RequestBody ReportInput input) {
    validateReport(input);
    Item created = items.create(input);
    matching.matchNewItem(created.id());
    return ResponseEntity.status(HttpStatus.CREATED).body(created);
  }

  @GetMapping("/matches")
  public List<Match> getMatches() {
    return matches.list();
  }

  @PostMapping("/matches/{matchId}/verify")
  public VerificationResult verify(
      @PathVariable int matchId,
      @RequestBody VerificationInput input
  ) {
    requireText(input == null ? null : input.privateDetail(), "Private detail", 180);
    return matching.verify(matchId, input.privateDetail());
  }

  @GetMapping("/matches/{matchId}/messages")
  public List<Message> getMessages(@PathVariable int matchId) {
    requireVerified(matchId);
    return messages.list(matchId);
  }

  @PostMapping("/matches/{matchId}/messages")
  public ResponseEntity<Message> sendMessage(
      @PathVariable int matchId,
      @RequestBody MessageInput input
  ) {
    requireVerified(matchId);
    validateMessage(input);
    return ResponseEntity.status(HttpStatus.CREATED).body(messages.create(matchId, input));
  }

  @PostMapping("/matches/{matchId}/confirm-return")
  public Match confirmReturn(
      @PathVariable int matchId,
      @RequestBody ReturnConfirmationInput input
  ) {
    String role = input == null ? "" : normalized(input.role());
    if (!role.equals("OWNER") && !role.equals("FINDER")) {
      throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Choose owner or finder.");
    }
    requireVerified(matchId);
    matches.confirmReturn(matchId, role);
    return matches.requirePublic(matchId);
  }

  private void validateReport(ReportInput input) {
    if (input == null) {
      throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Report details are required.");
    }
    String type = normalized(input.type());
    if (!type.equals("LOST") && !type.equals("FOUND")) {
      throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Choose lost or found.");
    }
    requireText(input.reporter(), "Name", MAX_NAME_LENGTH);
    requireText(input.title(), "Item name", 140);
    requireText(input.category(), "Category", 64);
    requireText(input.description(), "Description", 1000);
    requireText(input.location(), "Location", 180);
    requireText(input.itemDate(), "Date and time", 60);
    try {
      String date = input.itemDate().trim();
      if (date.length() == 10) {
        LocalDate.parse(date);
      } else {
        Instant.parse(date);
      }
    } catch (Exception exception) {
      throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Use a valid date and time.");
    }
    if (type.equals("LOST")) {
      requireText(input.privateDetail(), "Private verification detail", 180);
    }
    if (input.photoUrl() != null && !input.photoUrl().isBlank()) {
      try {
        URI photo = URI.create(input.photoUrl().trim());
        if (!"https".equalsIgnoreCase(photo.getScheme()) && !"http".equalsIgnoreCase(photo.getScheme())) {
          throw new IllegalArgumentException("Unsupported image URL.");
        }
      } catch (IllegalArgumentException exception) {
        throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Photo must be a valid web URL.");
      }
    }
  }

  private void validateMessage(MessageInput input) {
    if (input == null) {
      throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Message details are required.");
    }
    String role = normalized(input.role());
    if (!role.equals("OWNER") && !role.equals("FINDER")) {
      throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Choose owner or finder.");
    }
    requireText(input.senderName(), "Name", MAX_NAME_LENGTH);
    requireText(input.text(), "Message", 1000);
  }

  private void requireVerified(int matchId) {
    Match match = matches.requirePublic(matchId);
    if (!match.verified()) {
      throw new ResponseStatusException(
          HttpStatus.FORBIDDEN, "Verify ownership before opening this chat.");
    }
  }

  private static void requireText(String value, String label, int maxLength) {
    if (value == null || value.isBlank()) {
      throw new ResponseStatusException(HttpStatus.BAD_REQUEST, label + " is required.");
    }
    if (value.trim().length() > maxLength) {
      throw new ResponseStatusException(HttpStatus.BAD_REQUEST, label + " is too long.");
    }
  }

  private static String normalized(String value) {
    return value == null ? "" : value.trim().toUpperCase(Locale.ROOT);
  }

  private int count(String sql) {
    Integer result = jdbc.queryForObject(sql, Integer.class);
    return result == null ? 0 : result;
  }
}

@RestControllerAdvice
class FindItErrorHandler {
  @ExceptionHandler(ResponseStatusException.class)
  ResponseEntity<ErrorResponse> handleStatus(ResponseStatusException exception) {
    String reason = exception.getReason() == null ? "Request could not be completed." : exception.getReason();
    return ResponseEntity.status(exception.getStatusCode()).body(new ErrorResponse(reason));
  }
}
