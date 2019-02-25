package cc.roja.photo.model;

import org.apache.log4j.Logger;

import java.util.UUID;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import static java.lang.String.format;

/**
 * This class is responsible for enforcing the structure of an identifier for a media item when receiving it for processing.
 *
 * A media identifier is of this form:
 *     /[USER_ID]/[yyyy]/[yyyy-mm-dd]/[yyyy-mm-ddThhmmss]_[SLUG-8].[EXT]
 *               ^------------------FILEPATH---------------------------^
 *                                    ^---------FILENAME---------------^
 *
 * For example:
 *     /2d249780-7fe9-4c49-aa31-0a30d56afa0f/2020/2020-02-26/2020-02-26T000000_4y5k48k7.jpg
 */
@SuppressWarnings("unused")
public class ImageKey {
  private static final Logger LOG = Logger.getLogger(ImageKey.class);

  private UUID userId;
  private String filePath;
  private String filename;

  public void parse(String imageIdentifier) {
    //noinspection RegExpRedundantEscape
    String regex = "^[/](?<userId>[0-9a-fA-F]{8}\\-[0-9a-fA-F]{4}\\-[0-9a-fA-F]{4}\\-[0-9a-fA-F]{4}\\-[0-9a-fA-F]{12})[/](?<collection>[0-9]{4})[/](?<album>[0-9]{4}[-]?[0-9]{2}[-]?[0-9]{0,2}[_A-Za-z0-9- ,']*)[/](?<filename>[0-9]{4}[-]?[0-9]{2}[-]?[0-9]{0,2}T[0-9]{6}_[a-z0-9]{8}\\.[a-z]{3,4})";
    Pattern pattern = Pattern.compile(regex);
    Matcher matcher = pattern.matcher(imageIdentifier);
    boolean success = matcher.find();

    if(success) {
      String uid = matcher.group("userId");
      String collection = matcher.group("collection");
      String album = matcher.group("album");
      String filename = matcher.group("filename");

      LOG.debug("UserId: " + userId + ", Collection: "+collection+", Album: "+album+", Filename: "+filename);

      this.userId = UUID.fromString(uid);
      this.filePath = "/" + collection + "/" + album + "/" + filename;
      this.filename = filename;
    } else {
      throw new IllegalArgumentException(format("image identifier in unrecognized format [%s]", imageIdentifier));
    }
  }

  public UUID getUserId() {
    return userId;
  }

  public String getFilePath() {
    return filePath;
  }

  public String getFilename() {
    return filename;
  }

  public String getKey() {
    return "/" + this.userId + this.filePath;
  }

  public String toString() {
    return getKey();
  }
}
