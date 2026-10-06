package com.findit;

import com.findit.ApiModels.Item;
import com.findit.ApiModels.ReportInput;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.time.Instant;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.util.List;
import java.util.Optional;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.stereotype.Repository;

@Repository
public class ItemRepository {
  private static final RowMapper<StoredItem> ITEM_MAPPER = ItemRepository::mapItem;
  private final JdbcTemplate jdbc;

  public ItemRepository(JdbcTemplate jdbc) {
    this.jdbc = jdbc;
  }

  public Item create(ReportInput input) {
    String sql = """
        INSERT INTO findit_items
          (type, reporter, title, category, description, location, item_date, photo_url, private_detail)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        RETURNING id
        """;
    Integer id = jdbc.queryForObject(sql, Integer.class,
        input.type().trim().toUpperCase(),
        input.reporter().trim(),
        input.title().trim(),
        input.category().trim(),
        input.description().trim(),
        input.location().trim(),
        parseTimestamp(input.itemDate()),
        blankToNull(input.photoUrl()),
        input.privateDetail() == null ? "" : input.privateDetail().trim());
    if (id == null) {
      throw new IllegalStateException("The report was saved without an identifier.");
    }
    return requireStored(id).toPublicItem();
  }

  public List<Item> list(String type, String query, String status) {
    String search = query == null || query.isBlank() ? "" : "%" + query.trim().toLowerCase() + "%";
    return jdbc.query("""
        SELECT * FROM findit_items
        WHERE (? = '' OR type = ?)
          AND (? = '' OR status = ?)
          AND (? = '' OR LOWER(title) LIKE ? OR LOWER(description) LIKE ?
               OR LOWER(category) LIKE ? OR LOWER(location) LIKE ?)
        ORDER BY created_at DESC
        """,
        ITEM_MAPPER,
        value(type), value(type), value(status), value(status),
        search, search, search, search, search).stream().map(StoredItem::toPublicItem).toList();
  }

  public List<StoredItem> findOpenByOppositeType(String type) {
    String opposite = "LOST".equals(type) ? "FOUND" : "LOST";
    return jdbc.query(
        "SELECT * FROM findit_items WHERE type = ? AND status = 'OPEN' ORDER BY item_date DESC",
        ITEM_MAPPER, opposite);
  }

  public Optional<StoredItem> findStored(int id) {
    return jdbc.query("SELECT * FROM findit_items WHERE id = ?", ITEM_MAPPER, id)
        .stream().findFirst();
  }

  public StoredItem requireStored(int id) {
    return findStored(id).orElseThrow(() ->
        new org.springframework.web.server.ResponseStatusException(
            org.springframework.http.HttpStatus.NOT_FOUND, "Report not found"));
  }

  public void updateStatus(int id, String status) {
    jdbc.update("UPDATE findit_items SET status = ? WHERE id = ?", status, id);
  }

  public void updatePairStatus(int lostId, int foundId, String status) {
    jdbc.update("UPDATE findit_items SET status = ? WHERE id IN (?, ?)", status, lostId, foundId);
  }

  private static StoredItem mapItem(ResultSet rs, int row) throws SQLException {
    return new StoredItem(
        rs.getInt("id"),
        rs.getString("type"),
        rs.getString("reporter"),
        rs.getString("title"),
        rs.getString("category"),
        rs.getString("description"),
        rs.getString("location"),
        rs.getTimestamp("item_date").toInstant().toString(),
        rs.getString("photo_url"),
        rs.getString("private_detail"),
        rs.getString("status"),
        rs.getTimestamp("created_at").toInstant().toString()
    );
  }

  private static Timestamp parseTimestamp(String value) {
    try {
      return Timestamp.from(Instant.parse(value));
    } catch (Exception ignored) {
      try {
        return Timestamp.from(OffsetDateTime.parse(value).toInstant());
      } catch (Exception ignoredAgain) {
        try {
          return Timestamp.from(LocalDateTime.parse(value).toInstant(ZoneOffset.UTC));
        } catch (Exception ignoredDateTime) {
          return Timestamp.from(LocalDate.parse(value).atStartOfDay().toInstant(ZoneOffset.UTC));
        }
      }
    }
  }

  private static String value(String input) {
    return input == null ? "" : input.trim().toUpperCase();
  }

  private static String blankToNull(String value) {
    return value == null || value.isBlank() ? null : value.trim();
  }

  public record StoredItem(
      int id,
      String type,
      String reporter,
      String title,
      String category,
      String description,
      String location,
      String itemDate,
      String photoUrl,
      String privateDetail,
      String status,
      String createdAt
  ) {
    public Item toPublicItem() {
      return new Item(id, type, reporter, title, category, description, location,
          itemDate, photoUrl, status, createdAt);
    }
  }
}
