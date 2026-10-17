package com.findit;

import java.util.List;

public final class ApiModels {
  private ApiModels() {}

  public record Item(
      int id,
      String type,
      String reporter,
      String title,
      String category,
      String description,
      String location,
      String itemDate,
      String photoUrl,
      String status,
      String createdAt
  ) {}

  public record ReportInput(
      String type,
      String reporter,
      String title,
      String category,
      String description,
      String location,
      String itemDate,
      String photoUrl,
      String privateDetail
  ) {}

  public record Match(
      int id,
      Item lostItem,
      Item foundItem,
      double score,
      String status,
      boolean verified,
      boolean lostConfirmed,
      boolean foundConfirmed,
      String createdAt
  ) {}

  public record VerificationInput(String privateDetail) {}
  public record VerificationResult(boolean verified, String message, Match match) {}
  public record Message(int id, int matchId, String role, String senderName, String text, String sentAt) {}
  public record MessageInput(String role, String senderName, String text) {}
  public record ReturnConfirmationInput(String role) {}

  public record DashboardSummary(
      int totalReports,
      int lostReports,
      int foundReports,
      int openReports,
      int potentialMatches,
      int returnedItems
  ) {}

  public record SignupInput(
      String fullName,
      String email,
      String password,
      String confirmPassword
  ) {}

  public record LoginInput(
      String email,
      String password
  ) {}

  public record AuthResponse(
      int id,
      String fullName,
      String email,
      String token
  ) {}

  public record UserProfile(
      int id,
      String fullName,
      String email,
      String createdAt
  ) {}

  public record HealthStatus(String status) {}
  public record ErrorResponse(String error) {}
}
