package com.findit;

import com.findit.ApiModels.Match;
import com.findit.ApiModels.VerificationResult;
import com.findit.ItemRepository.StoredItem;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.time.Duration;
import java.time.Instant;
import java.util.Arrays;
import java.util.HashSet;
import java.util.Locale;
import java.util.Set;
import java.util.stream.Collectors;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

@Service
public class MatchingService {
  private static final double MATCH_THRESHOLD = 0.34;
  private static final Set<String> COMMON_WORDS = Set.of(
      "a", "an", "and", "at", "by", "found", "for", "from", "i", "in", "is",
      "it", "lost", "near", "of", "on", "the", "to", "with"
  );

  private final ItemRepository items;
  private final MatchRepository matches;

  public MatchingService(ItemRepository items, MatchRepository matches) {
    this.items = items;
    this.matches = matches;
  }

  public void matchNewItem(int itemId) {
    StoredItem current = items.requireStored(itemId);
    for (StoredItem candidate : items.findOpenByOppositeType(current.type())) {
      StoredItem lost = "LOST".equals(current.type()) ? current : candidate;
      StoredItem found = "FOUND".equals(current.type()) ? current : candidate;
      double score = score(lost, found);
      if (score >= MATCH_THRESHOLD && matches.createIfAbsent(lost.id(), found.id(), score)) {
        items.updateStatus(lost.id(), "MATCHED");
        items.updateStatus(found.id(), "MATCHED");
      }
    }
  }

  public VerificationResult verify(int matchId, String submittedDetail) {
    MatchRepository.MatchRow row = matches.findRow(matchId).orElseThrow(() ->
        new ResponseStatusException(HttpStatus.NOT_FOUND, "Match not found"));
    if (!row.verified()) {
      String expected = normalize(items.requireStored(row.lostItemId()).privateDetail());
      String actual = normalize(submittedDetail);
      boolean correct = !expected.isBlank()
          && MessageDigest.isEqual(expected.getBytes(StandardCharsets.UTF_8),
              actual.getBytes(StandardCharsets.UTF_8));
      if (!correct) {
        return new VerificationResult(false,
            "That detail did not match. Check the private detail from your lost report and try again.",
            matches.requirePublic(matchId));
      }
      matches.markVerified(matchId);
    }
    Match verifiedMatch = matches.requirePublic(matchId);
    return new VerificationResult(true,
        "Ownership verified. The in-app chat is now available.", verifiedMatch);
  }

  private static double score(StoredItem lost, StoredItem found) {
    Instant lostAt = Instant.parse(lost.itemDate());
    Instant foundAt = Instant.parse(found.itemDate());
    if (foundAt.isBefore(lostAt)) {
      return 0;
    }

    double category = lost.category().equalsIgnoreCase(found.category()) ? 1.0 : 0.0;
    double text = jaccard(
        lost.title() + " " + lost.description(),
        found.title() + " " + found.description()
    );
    double location = lost.location().equalsIgnoreCase(found.location())
        ? 1.0
        : jaccard(lost.location(), found.location());
    double daysApart = Duration.between(lostAt, foundAt).toSeconds() / 86_400.0;
    double time = Math.max(0.0, 1.0 - (daysApart / 30.0));

    return (0.25 * category) + (0.45 * text) + (0.20 * location) + (0.10 * time);
  }

  private static double jaccard(String first, String second) {
    Set<String> a = tokens(first);
    Set<String> b = tokens(second);
    if (a.isEmpty() || b.isEmpty()) {
      return 0.0;
    }
    Set<String> intersection = new HashSet<>(a);
    intersection.retainAll(b);
    Set<String> union = new HashSet<>(a);
    union.addAll(b);
    return (double) intersection.size() / union.size();
  }

  private static Set<String> tokens(String value) {
    return Arrays.stream(value.toLowerCase(Locale.ROOT).split("[^a-z0-9]+"))
        .filter(token -> token.length() > 1 && !COMMON_WORDS.contains(token))
        .collect(Collectors.toSet());
  }

  private static String normalize(String value) {
    return value == null
        ? ""
        : value.toLowerCase(Locale.ROOT).replaceAll("[^a-z0-9]", "");
  }
}
