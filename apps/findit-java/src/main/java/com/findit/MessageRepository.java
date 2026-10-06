package com.findit;

import com.findit.ApiModels.Message;
import com.findit.ApiModels.MessageInput;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.List;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.stereotype.Repository;

@Repository
public class MessageRepository {
  private static final RowMapper<Message> MESSAGE_MAPPER = MessageRepository::mapMessage;
  private final JdbcTemplate jdbc;

  public MessageRepository(JdbcTemplate jdbc) {
    this.jdbc = jdbc;
  }

  public List<Message> list(int matchId) {
    return jdbc.query(
        "SELECT * FROM findit_messages WHERE match_id = ? ORDER BY sent_at ASC",
        MESSAGE_MAPPER, matchId);
  }

  public Message create(int matchId, MessageInput input) {
    return jdbc.queryForObject("""
        INSERT INTO findit_messages (match_id, role, sender_name, text)
        VALUES (?, ?, ?, ?)
        RETURNING *
        """, MESSAGE_MAPPER,
        matchId, input.role().trim().toUpperCase(), input.senderName().trim(), input.text().trim());
  }

  private static Message mapMessage(ResultSet rs, int row) throws SQLException {
    return new Message(
        rs.getInt("id"),
        rs.getInt("match_id"),
        rs.getString("role"),
        rs.getString("sender_name"),
        rs.getString("text"),
        rs.getTimestamp("sent_at").toInstant().toString()
    );
  }
}
