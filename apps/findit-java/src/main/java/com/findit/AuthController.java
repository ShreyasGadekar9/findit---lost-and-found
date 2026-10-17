package com.findit;

import com.findit.ApiModels.AuthResponse;
import com.findit.ApiModels.LoginInput;
import com.findit.ApiModels.SignupInput;
import com.findit.ApiModels.UserProfile;
import com.findit.UserRepository.UserRecord;
import java.util.Optional;
import java.util.regex.Pattern;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

@RestController
@RequestMapping("/auth")
public class AuthController {
  private static final Pattern EMAIL_PATTERN = Pattern.compile("^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$");
  private static final Pattern UPPER_PATTERN = Pattern.compile("[A-Z]");
  private static final Pattern LOWER_PATTERN = Pattern.compile("[a-z]");
  private static final Pattern DIGIT_PATTERN = Pattern.compile("[0-9]");
  private static final Pattern SPECIAL_PATTERN = Pattern.compile("[!@#$%^&*()_+\\-=\\[\\]{};':\"\\\\|,.<>/?]");

  private final UserRepository users;

  public AuthController(UserRepository users) {
    this.users = users;
  }

  @PostMapping("/signup")
  public ResponseEntity<AuthResponse> signup(@RequestBody SignupInput input) {
    validateSignupInput(input);

    String normalizedEmail = input.email().trim().toLowerCase();
    if (users.existsByEmail(normalizedEmail)) {
      throw new ResponseStatusException(HttpStatus.CONFLICT, "An account with this email address already exists.");
    }

    String salt = PasswordUtils.generateSalt();
    String passwordHash = PasswordUtils.hashPassword(input.password(), salt);

    UserProfile user = users.create(input.fullName().trim(), normalizedEmail, passwordHash, salt);
    String token = PasswordUtils.generateSessionToken();
    users.createSession(token, user.id());

    return ResponseEntity.status(HttpStatus.CREATED)
        .body(new AuthResponse(user.id(), user.fullName(), user.email(), token));
  }

  @PostMapping("/login")
  public ResponseEntity<AuthResponse> login(@RequestBody LoginInput input) {
    if (input == null || input.email() == null || input.password() == null) {
      throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Email and password are required.");
    }

    String normalizedEmail = input.email().trim().toLowerCase();
    Optional<UserRecord> optionalUser = users.findByEmail(normalizedEmail);

    if (optionalUser.isEmpty()) {
      throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Invalid email or password.");
    }

    UserRecord userRecord = optionalUser.get();
    boolean matches = PasswordUtils.verifyPassword(input.password(), userRecord.passwordHash(), userRecord.salt());

    if (!matches) {
      throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Invalid email or password.");
    }

    String token = PasswordUtils.generateSessionToken();
    users.createSession(token, userRecord.id());

    return ResponseEntity.ok(new AuthResponse(userRecord.id(), userRecord.fullName(), userRecord.email(), token));
  }

  @GetMapping("/me")
  public ResponseEntity<UserProfile> me(
      @RequestHeader(name = "Authorization", required = false) String authHeader,
      @RequestHeader(name = "X-Auth-Token", required = false) String customHeader,
      @RequestParam(name = "token", required = false) String tokenParam
  ) {
    String token = extractToken(authHeader, customHeader, tokenParam);
    if (token == null || token.isBlank()) {
      throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Not authenticated.");
    }

    UserProfile profile = users.findProfileBySessionToken(token)
        .orElseThrow(() -> new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Invalid or expired session token."));

    return ResponseEntity.ok(profile);
  }

  @PostMapping("/logout")
  public ResponseEntity<Void> logout(
      @RequestHeader(name = "Authorization", required = false) String authHeader,
      @RequestHeader(name = "X-Auth-Token", required = false) String customHeader,
      @RequestParam(name = "token", required = false) String tokenParam
  ) {
    String token = extractToken(authHeader, customHeader, tokenParam);
    if (token != null && !token.isBlank()) {
      users.deleteSession(token);
    }
    return ResponseEntity.ok().build();
  }

  private void validateSignupInput(SignupInput input) {
    if (input == null) {
      throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Registration details are required.");
    }

    String name = input.fullName() == null ? "" : input.fullName().trim();
    if (name.isBlank()) {
      throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Full name is required.");
    }
    if (name.length() > 100) {
      throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Full name must be 100 characters or less.");
    }

    String email = input.email() == null ? "" : input.email().trim();
    if (email.isBlank()) {
      throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Email address is required.");
    }
    if (email.length() > 120 || !EMAIL_PATTERN.matcher(email).matches()) {
      throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Please enter a valid email address.");
    }

    String password = input.password();
    if (password == null || password.isBlank()) {
      throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Password is required.");
    }
    if (password.length() < 8) {
      throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Password must be at least 8 characters long.");
    }
    if (password.length() > 100) {
      throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Password is too long.");
    }

    if (!UPPER_PATTERN.matcher(password).find()
        || !LOWER_PATTERN.matcher(password).find()
        || !DIGIT_PATTERN.matcher(password).find()
        || !SPECIAL_PATTERN.matcher(password).find()) {
      throw new ResponseStatusException(
          HttpStatus.BAD_REQUEST,
          "Password must include at least one uppercase letter, one lowercase letter, one number, and one special character."
      );
    }

    String confirm = input.confirmPassword();
    if (confirm == null || !confirm.equals(password)) {
      throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Passwords do not match.");
    }
  }

  private String extractToken(String authHeader, String customHeader, String tokenParam) {
    if (authHeader != null && authHeader.toLowerCase().startsWith("bearer ")) {
      return authHeader.substring(7).trim();
    }
    if (customHeader != null && !customHeader.isBlank()) {
      return customHeader.trim();
    }
    if (tokenParam != null && !tokenParam.isBlank()) {
      return tokenParam.trim();
    }
    return null;
  }
}
