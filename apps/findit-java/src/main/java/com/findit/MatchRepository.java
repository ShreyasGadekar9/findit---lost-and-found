package com.findit;

import com.findit.ApiModels.Item;
import com.findit.ApiModels.Match;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.List;
import java.util.Optional;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.stereotype.Repository;

@Repository
public class MatchRepository {
  private static final RowMapper<MatchRow> MATCH_MAPPER = MatchRepository::mapMatch;
  private final JdbcTemplate jdbc;
  private final ItemRepository items;

  public MatchRepository(JdbcTemplate jdbc, ItemRepository items) {
    this.jdbc = jdbc;
    this.items = items;
  }

  public boolean createIfAbsent(int lostId, int foundId, double score) {
    return jdbc.update("""
        INSERT INTO findit_matches (lost_item_id, found_item_id, score)
        VALUES (?, ?, ?)
        ON CONFLICT (lost_item_id, found_item_id) DO NOTHING
        """, lostId, foundId, score) > 0;
  }

  public List<Match> list() {
    return jdbc.query("SELECT * FROM findit_matches ORDER BY score DESC, created_at DESC", MATCH_MAPPER)
        .stream().map(this::toPublicMatch).toList();
  }

  public Optional<Match> findPublic(int id) {
    return findRow(id).map(this::toPublicMatch);
  }

  public Match requirePublic(int id) {
    return findPublic(id).orElseThrow(() ->
        new org.springframework.web.server.ResponseStatusException(
            org.springframework.http.HttpStatus.NOT_FOUND, "Match not found"));
  }

  public Optional<MatchRow> findRow(int id) {
    return jdbc.query("SELECT * FROM findit_matches WHERE id = ?", MATCH_MAPPER, id)
        .stream().findFirst();
  }

  public void markVerified(int id) {
    jdbc.update("UPDATE findit_matches SET verified = TRUE WHERE id = ?", id);
  }

  public void confirmReturn(int id, String role) {
    if ("OWNER".equals(role)) {
      jdbc.update("UPDATE findit_matches SET lost_confirmed = TRUE WHERE id = ?", id);
    } else {
      jdbc.update("UPDATE findit_matches SET found_confirmed = TRUE WHERE id = ?", id);
    }
    MatchRow match = findRow(id).orElseThrow(() ->
        new org.springframework.web.server.ResponseStatusException(
            org.springframework.http.HttpStatus.NOT_FOUND, "Match not found"));
    if (match.lostConfirmed() && match.foundConfirmed()) {
      jdbc.update("UPDATE findit_items SET status = 'RETURNED' WHERE id IN (?, ?)",
          match.lostItemId(), match.foundItemId());
    }
  }

  private Match toPublicMatch(MatchRow row) {
    Item lost = items.requireStored(row.lostItemId()).toPublicItem();
    Item found = items.requireStored(row.foundItemId()).toPublicItem();
    String status = row.lostConfirmed() && row.foundConfirmed()
        ? "RETURNED"
        : row.verified() ? "VERIFIED" : "POTENTIAL";
    return new Match(row.id(), lost, found, row.score(), status, row.verified(),
        row.lostConfirmed(), row.foundConfirmed(), row.createdAt());
  }

  private static MatchRow mapMatch(ResultSet rs, int row) throws SQLException {
    return new MatchRow(
        rs.getInt("id"),
        rs.getInt("lost_item_id"),
        rs.getInt("found_item_id"),
        rs.getDouble("score"),
        rs.getBoolean("verified"),
        rs.getBoolean("lost_confirmed"),
        rs.getBoolean("found_confirmed"),
        rs.getTimestamp("created_at").toInstant().toString()
    );
  }

  public record MatchRow(
      int id,
      int lostItemId,
      int foundItemId,
      double score,
      boolean verified,
      boolean lostConfirmed,
      boolean foundConfirmed,
      String createdAt
  ) {}
}
