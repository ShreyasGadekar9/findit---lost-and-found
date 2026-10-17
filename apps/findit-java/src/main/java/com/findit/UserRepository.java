package com.findit;

import com.findit.ApiModels.UserProfile;
import java.sql.PreparedStatement;
import java.sql.Statement;
import java.time.Instant;
import java.util.Optional;
import org.springframework.dao.EmptyResultDataAccessException;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.jdbc.support.GeneratedKeyHolder;
import org.springframework.jdbc.support.KeyHolder;
import org.springframework.stereotype.Repository;

@Repository
public class UserRepository {
  private final JdbcTemplate jdbc;

  public UserRepository(JdbcTemplate jdbc) {
    this.jdbc = jdbc;
  }

  public record UserRecord(
      int id,
      String fullName,
      String email,
      String passwordHash,
      String salt,
      Instant createdAt
  ) {}

  private static final RowMapper<UserRecord> USER_RECORD_MAPPER = (rs, rowNum) -> new UserRecord(
      rs.getInt("id"),
      rs.getString("full_name"),
      rs.getString("email"),
      rs.getString("password_hash"),
      rs.getString("salt"),
      rs.getTimestamp("created_at").toInstant()
  );

  private static final RowMapper<UserProfile> USER_PROFILE_MAPPER = (rs, rowNum) -> new UserProfile(
      rs.getInt("id"),
      rs.getString("full_name"),
      rs.getString("email"),
      rs.getTimestamp("created_at").toInstant().toString()
  );

  public boolean existsByEmail(String email) {
    if (email == null) return false;
    Integer count = jdbc.queryForObject(
        "SELECT COUNT(*) FROM findit_users WHERE LOWER(email) = LOWER(?)",
        Integer.class,
        email.trim()
    );
    return count != null && count > 0;
  }

  public UserProfile create(String fullName, String email, String passwordHash, String salt) {
    KeyHolder keyHolder = new GeneratedKeyHolder();
    jdbc.update(connection -> {
      PreparedStatement ps = connection.prepareStatement(
          "INSERT INTO findit_users (full_name, email, password_hash, salt) VALUES (?, ?, ?, ?)",
          Statement.RETURN_GENERATED_KEYS
      );
      ps.setString(1, fullName.trim());
      ps.setString(2, email.trim().toLowerCase());
      ps.setString(3, passwordHash);
      ps.setString(4, salt);
      return ps;
    }, keyHolder);

    Number key = keyHolder.getKey();
    int id = key != null ? key.intValue() : 0;
    return findProfileById(id).orElseThrow(() -> new RuntimeException("Failed to retrieve created user profile"));
  }

  public Optional<UserRecord> findByEmail(String email) {
    if (email == null) return Optional.empty();
    try {
      UserRecord user = jdbc.queryForObject(
          "SELECT id, full_name, email, password_hash, salt, created_at FROM findit_users WHERE LOWER(email) = LOWER(?)",
          USER_RECORD_MAPPER,
          email.trim()
      );
      return Optional.ofNullable(user);
    } catch (EmptyResultDataAccessException e) {
      return Optional.empty();
    }
  }

  public Optional<UserProfile> findProfileById(int id) {
    try {
      UserProfile user = jdbc.queryForObject(
          "SELECT id, full_name, email, created_at FROM findit_users WHERE id = ?",
          USER_PROFILE_MAPPER,
          id
      );
      return Optional.ofNullable(user);
    } catch (EmptyResultDataAccessException e) {
      return Optional.empty();
    }
  }

  public void createSession(String token, int userId) {
    jdbc.update("INSERT INTO findit_sessions (token, user_id) VALUES (?, ?)", token, userId);
  }

  public Optional<UserProfile> findProfileBySessionToken(String token) {
    if (token == null || token.isBlank()) return Optional.empty();
    try {
      UserProfile profile = jdbc.queryForObject(
          """
          SELECT u.id, u.full_name, u.email, u.created_at
          FROM findit_users u
          JOIN findit_sessions s ON u.id = s.user_id
          WHERE s.token = ?
          """,
          USER_PROFILE_MAPPER,
          token.trim()
      );
      return Optional.ofNullable(profile);
    } catch (EmptyResultDataAccessException e) {
      return Optional.empty();
    }
  }

  public void deleteSession(String token) {
    if (token == null || token.isBlank()) return;
    jdbc.update("DELETE FROM findit_sessions WHERE token = ?", token.trim());
  }
}
