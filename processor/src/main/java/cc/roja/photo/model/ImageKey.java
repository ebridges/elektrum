package cc.roja.photo.model;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import java.util.UUID;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import static java.lang.String.format;

/**
 * This class is responsible for enforcing the structure of an identifier for a media item when receiving it for processing.
 *
 * A media identifier is of this form:
 *     /[USER_ID]/[UUID4].[EXT]
 *
 * For example:
 *     /2d249780-7fe9-4c49-aa31-0a30d56afa0f/6ee17b58-7008-11e9-a612-320017981ea0.jpg
 */
public class ImageKey {
  private static final Logger LOG = LogManager.getLogger(ImageKey.class);

  private UUID userId;
  private UUID imageId;
  private String filename;

  public static ImageKey parse(String imageIdentifier) {
    //noinspection RegExpRedundantEscape
    String regex = "^[/](?<userId>[0-9a-fA-F]{8}\\-[0-9a-fA-F]{4}\\-[0-9a-fA-F]{4}\\-[0-9a-fA-F]{4}\\-[0-9a-fA-F]{12})[/](?<imageId>[0-9a-fA-F]{8}\\-[0-9a-fA-F]{4}\\-[0-9a-fA-F]{4}\\-[0-9a-fA-F]{4}\\-[0-9a-fA-F]{12})\\.(?<extension>[a-z]{3,4})";
    Pattern pattern = Pattern.compile(regex);
    Matcher matcher = pattern.matcher(imageIdentifier);
    boolean success = matcher.find();

    if(success) {
      String uid = matcher.group("userId");
      String iid = matcher.group("imageId");
      String ext = matcher.group("extension");
      String filename = iid + '.' + ext;

      LOG.debug("UserId: " + uid + ", Filename: "+filename);

      return new ImageKey(UUID.fromString(uid), UUID.fromString(iid), filename);
    } else {
      throw new IllegalArgumentException(format("image identifier in unrecognized format [%s]", imageIdentifier));
    }
  }

  private ImageKey(UUID userId, UUID imageId, String filename) {
    this.userId = userId;
    this.imageId = imageId;
    this.filename = filename;
  }

  public UUID getUserId() {
    return userId;
  }

  public UUID getImageId() { return imageId; }

  public String getFilename() {
    return filename;
  }

  public String getKey() {
    return "/" + this.userId + "/" + this.filename;
  }

  public String toString() {
    return getKey();
  }
}
