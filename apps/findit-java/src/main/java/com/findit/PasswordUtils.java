package com.findit;

import java.security.NoSuchAlgorithmException;
import java.security.SecureRandom;
import java.security.spec.InvalidKeySpecException;
import java.security.spec.KeySpec;
import java.util.Base64;
import java.util.HexFormat;
import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.PBEKeySpec;

public final class PasswordUtils {
  private static final int SALT_LENGTH = 16;
  private static final int ITERATIONS = 65536;
  private static final int KEY_LENGTH = 256;
  private static final SecureRandom RANDOM = new SecureRandom();

  private PasswordUtils() {}

  public static String generateSalt() {
    byte[] salt = new byte[SALT_LENGTH];
    RANDOM.nextBytes(salt);
    return HexFormat.of().formatHex(salt);
  }

  public static String hashPassword(String password, String saltHex) {
    try {
      byte[] salt = HexFormat.of().parseHex(saltHex);
      KeySpec spec = new PBEKeySpec(password.toCharArray(), salt, ITERATIONS, KEY_LENGTH);
      SecretKeyFactory factory = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256");
      byte[] hash = factory.generateSecret(spec).getEncoded();
      return HexFormat.of().formatHex(hash);
    } catch (NoSuchAlgorithmException | InvalidKeySpecException e) {
      throw new RuntimeException("Error hashing password securely", e);
    }
  }

  public static boolean verifyPassword(String password, String storedHash, String storedSaltHex) {
    String hash = hashPassword(password, storedSaltHex);
    return constantTimeEquals(hash, storedHash);
  }

  private static boolean constantTimeEquals(String a, String b) {
    if (a == null || b == null) return false;
    byte[] aBytes = a.getBytes();
    byte[] bBytes = b.getBytes();
    if (aBytes.length != bBytes.length) return false;
    int result = 0;
    for (int i = 0; i < aBytes.length; i++) {
      result |= aBytes[i] ^ bBytes[i];
    }
    return result == 0;
  }

  public static String generateSessionToken() {
    byte[] tokenBytes = new byte[32];
    RANDOM.nextBytes(tokenBytes);
    return Base64.getUrlEncoder().withoutPadding().encodeToString(tokenBytes);
  }
}
