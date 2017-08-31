package cc.roja.photo;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.time.LocalDate;
import java.time.YearMonth;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.skife.jdbi.v2.DBI;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestHandler;
import com.amazonaws.services.s3.event.S3EventNotification;

import org.apache.log4j.Logger;

@SuppressWarnings({"unused","WeakerAccess"})
public class Processor implements RequestHandler<S3EventNotification, ProcessorResult> {
  private static final Logger LOG = Logger.getLogger(Processor.class);
  private static final DateTimeFormatter YYYY_MM_DD = DateTimeFormatter.ISO_DATE;

  private DBI dbi;

  public Processor() {
    this.dbi = DatabaseManager.getDBI();
  }

  public static void main(String[] args) throws IOException {
    String arg = args[0];

    Processor processor = new Processor();

    if("-f".equals(arg)) {
      processFiles(processor, args[1]);
    } else {
      processFile(processor, arg);
    }
  }

  private static void processFiles(Processor processor, String fileList) throws IOException {
    File fl = new File(fileList);
    FileReader frd = new FileReader(fl);
    try(BufferedReader brd = new BufferedReader(frd)) {
      String imageKey;
      while ((imageKey = brd.readLine()) != null) {
        String imageId = processor.processPhoto(imageKey);
      }
    }
  }

  private static void processFile(Processor processor, String imageKey) throws IOException {
    String imageId = processor.processPhoto(imageKey);
    LOG.info("imageId: " + imageId);
  }

  /*
  Example event:
  ```
    {
      "Records":[
        {
          "eventVersion":"2.0",
          "eventSource":"aws:s3",
          "awsRegion":"us-west-2",
          "eventTime":"1970-01-01T00:00:00.000Z",
          "eventName":"ObjectCreated:Put",
          "userIdentity":{
             "principalId":"AIDAJDPLRKLG7UEXAMPLE"
          },
          "requestParameters":{
             "sourceIPAddress":"127.0.0.1"
          },
          "responseElements":{
             "x-amz-request-id":"C3D13FE58DE4C810",
             "x-amz-id-2":"FMyUVURIY8/IgAtTv8xRjskZQpcIZ9KG4V5Wp6S7S/JRWeUWerMUE5JgHvANOjpD"
          },
          "s3":{
             "s3SchemaVersion":"1.0",
             "configurationId":"testConfigRule",
             "bucket":{
                "name":"sourcebucket",
                "ownerIdentity":{
                   "principalId":"A3NL1KOZZKExample"
                },
                "arn":"arn:aws:s3:::sourcebucket"
             },
             "object":{
                "key":"HappyFace.jpg",
                "size":1024,
                "eTag":"d41d8cd98f00b204e9800998ecf8427e",
                "versionId":"096fKKXTRTtl3on89fVO.nfljtsv6qko"
              }
           }
         }
      ]
    }
    ```
   */

  @Override
  public ProcessorResult handleRequest(S3EventNotification event, Context context) {
    try {
      ProcessorResult result = new ProcessorResult();
      List<String> imageKeys = new ArrayList<>();

      for(S3EventNotification.S3EventNotificationRecord record : event.getRecords()) {
        S3EventNotification.S3Entity s3Entity = record.getS3();
        imageKeys.add(s3Entity.getObject().getKey());
      }

      for(String imageKey : imageKeys) {
        if (imageKey == null || imageKey.isEmpty()) {
          throw new IllegalArgumentException("missing imageKey");
        }

        String imageId = processPhoto(imageKey);
        result.addImageId(imageId);
      }

      return result;
    } catch (IOException e) {
      throw new IllegalArgumentException(e);
    }
  }

  public String processPhoto(String imageKey) throws IOException {
    try (PhotoProcessorDAO dao = dbi.open(PhotoProcessorDAO.class)) {
      String id = dao.queryByPath(imageKey);
      if(id != null) {
        LOG.info(String.format("Skipping: [%s]", imageKey));
        return id;
      }
      LOG.info("Processing: " + imageKey);
      MetaDataExtractor metaDataExtractor = new MetaDataExtractor();

      File imageFile = ImageLoader.load(imageKey);

      List<String> keyInfo = parseKey(imageKey);
      String collectionId = getCollection(dao, keyInfo.get(0));
      AlbumInfo albumInfo = getAlbum(dao, collectionId, keyInfo.get(0) + keyInfo.get(1));

      ImageInfo imageInfo = new ImageInfo(albumInfo);
      metaDataExtractor.extract(imageFile, imageInfo);

      String artistName = imageInfo.getArtist();
      String artistId = getArtist(dao, artistName);

      return dao.getOrCreateImage(keyInfo.get(2), imageKey, imageInfo, albumInfo.getId(), artistId);
    }
  }

  private String getArtist(PhotoProcessorDAO dao, String artistName) {
    String artistId = null;
    if(artistName != null) {
      artistId = dao.getOrCreateArtist(artistName);
    }
    return artistId;
  }

  private AlbumInfo getAlbum(PhotoProcessorDAO dao, String collectionId, String path) {
    String regex = "(?<name>(?<date>[0-9]{4}[-]?[0-9]{2}[-]?[0-9]{0,2})(?<caption>[_A-Za-z0-9- ,']*))$";
    Pattern pattern = Pattern.compile(regex);
    Matcher matcher = pattern.matcher(path);
    boolean success = matcher.find();
    if(!success) {
      throw new IllegalArgumentException("invalid album path: "+path);
    }

    String name = matcher.group("name");
    String date = matcher.group("date");
    String caption = matcher.group("caption");

    AlbumInfo albumInfo = albumInfo(name, path, date, caption, collectionId);

    String id = dao.getOrCreateAlbum(albumInfo);
    albumInfo.setId(id);

    return albumInfo;
  }

  private AlbumInfo albumInfo(String name, String path, String date, String caption, String collectionId) {
    LocalDate albumDate = parseDate(date);
    String albumCaption = null;
    if(caption != null && !caption.isEmpty()) {
      albumCaption = caption.replace("_", " ").trim();
    }

    return new AlbumInfo(
        name,
        path,
        albumCaption,
        null, // no source for this at this time.
        albumDate,
        collectionId
    );
  }

  private LocalDate parseDate(String date) {
    String[] yymmddFormats = new String[]{"yyyyMMdd'T'HHmmss", "yyyy-MM-dd'T'HHmmss", "yyyy-MM-dd", "yyyyMMdd"};
    for (String format : yymmddFormats) {
      DateTimeFormatter formatter = DateTimeFormatter.ofPattern(format);
      try {
        return LocalDate.parse(date, formatter);
      } catch(DateTimeParseException ignored) {
        // pass
      }
    }

    String[] yymmFormats = new String[]{"yyyyMM", "yyyy-MM"};
    for (String format : yymmFormats) {
      DateTimeFormatter formatter = DateTimeFormatter.ofPattern(format);
      try {
        YearMonth yyyyMM = YearMonth.parse(date, formatter);
        return LocalDate.of(yyyyMM.getYear(), yyyyMM.getMonth(), 1);
      } catch(DateTimeParseException ignored) {
        LOG.warn("exception: "+ignored.getMessage(), ignored);
      }
    }

    return null;
  }

  private String getCollection(PhotoProcessorDAO dao, String path) {
    if(!path.matches("^/[0-9]{4}$")) {
      throw new IllegalArgumentException("invalid collection path: "+path);
    }

    String name = path.substring(1);
    return dao.getOrCreateCollection(name, path);
  }

  private List<String> parseKey(String imageKey) {
    // example key: "/2017/2017-08-22/20170822T113305_01.jpg"
    //              "/2003/20030522_Quebec_BikeTrip/dscn1650.jpg"
    // key structure: "/yyyy/yyyy-mm-dd/yyyymmddThhmm_##.jpg"

    String regex = "^(?<collection>[/][0-9]{4})(?<album>[/][0-9]{4}[-]?[0-9]{2}[-]?[0-9]{0,2}[_A-Za-z0-9- ,']*)(?<image>[/a-zA-Z0-9._]+)";

    Pattern pattern = Pattern.compile(regex);
    Matcher matcher = pattern.matcher(imageKey);
    boolean success = matcher.find();

    String collection = success ? matcher.group("collection") : null;
    String album = success ? matcher.group("album") : null;
    String image = success ? matcher.group("image") : null;

    LOG.debug("Collection: "+collection+", Album: "+album+", Image: "+image);

    return Arrays.asList( collection, album, image );
  }
}
