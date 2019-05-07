package cc.roja.photo.util;

import java.util.HashMap;
import java.util.Map;

public class Constants {
  public static final int SRID = 4326;

  public static final Map<String,String> MIME_TYPES = new HashMap<>();

  static {
    MIME_TYPES.put("jpg", "image/jpeg");
    MIME_TYPES.put("jpeg", "image/jpeg");
    MIME_TYPES.put("png", "image/png");
  }
}
