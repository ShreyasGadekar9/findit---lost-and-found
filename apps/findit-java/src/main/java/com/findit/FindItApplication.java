package com.findit;

import com.findit.ApiModels.ReportInput;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import org.springframework.boot.ApplicationRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.beans.factory.annotation.Value;

@SpringBootApplication
public class FindItApplication {
  public static void main(String[] args) {
    SpringApplication.run(FindItApplication.class, args);
  }

  @Bean
  ApplicationRunner seedExampleReports(
      JdbcTemplate jdbc,
      ItemRepository items,
      MatchingService matching,
      @Value("${findit.seed-demo:false}") boolean seedDemo
  ) {
    return args -> {
      if (!seedDemo) return;
      Integer count = jdbc.queryForObject("SELECT COUNT(*) FROM findit_items", Integer.class);
      if (count != null && count == 0) {
        Instant now = Instant.now();
        items.create(new ReportInput(
            "LOST", "Anaya S.", "Brown leather wallet", "Accessories",
            "Slim brown leather wallet with a brass snap closure.",
            "Central Library, East Entrance", now.minus(5, ChronoUnit.HOURS).toString(), null,
            "small blue stitch"
        ));
        int foundId = items.create(new ReportInput(
            "FOUND", "Rohan P.", "Found brown card wallet", "Accessories",
            "Brown leather wallet with brass snap, found by the library east entrance.",
            "Central Library, East Entrance", now.minus(2, ChronoUnit.HOURS).toString(), null,
            "two cards inside"
        )).id();
        matching.matchNewItem(foundId);
      }
    };
  }
}
