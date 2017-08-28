package cc.roja.photo;

import static cc.roja.photo.util.DateUtil.determineTimeZoneOffset;
import static cc.roja.photo.util.MetadataUtil.getDirectory;
import static cc.roja.photo.util.MetadataUtil.resolveRational;
import static cc.roja.photo.util.MetadataUtil.resolveString;
import static cc.roja.photo.util.TagPair.of;
import static com.drew.metadata.exif.ExifDirectoryBase.TAG_APERTURE;
import static com.drew.metadata.exif.ExifDirectoryBase.TAG_ARTIST;
import static com.drew.metadata.exif.ExifDirectoryBase.TAG_EXIF_IMAGE_HEIGHT;
import static com.drew.metadata.exif.ExifDirectoryBase.TAG_EXIF_IMAGE_WIDTH;
import static com.drew.metadata.exif.ExifDirectoryBase.TAG_EXPOSURE_TIME;
import static com.drew.metadata.exif.ExifDirectoryBase.TAG_FOCAL_LENGTH;
import static com.drew.metadata.exif.ExifDirectoryBase.TAG_ISO_EQUIVALENT;
import static com.drew.metadata.exif.ExifDirectoryBase.TAG_MAKE;
import static com.drew.metadata.exif.ExifDirectoryBase.TAG_MODEL;
import static com.drew.metadata.exif.GpsDirectory.TAG_ALTITUDE;

import java.io.File;
import java.io.IOException;
import java.time.LocalDate;
import java.time.LocalTime;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.apache.log4j.Logger;

import com.drew.imaging.ImageMetadataReader;
import com.drew.imaging.ImageProcessingException;
import com.drew.lang.GeoLocation;
import com.drew.lang.Rational;
import com.drew.metadata.Metadata;
import com.drew.metadata.exif.ExifIFD0Directory;
import com.drew.metadata.exif.ExifSubIFDDirectory;
import com.drew.metadata.exif.GpsDirectory;
import com.drew.metadata.file.FileMetadataDirectory;

import cc.roja.photo.util.MetadataUtil;

@SuppressWarnings("WeakerAccess")
public class MetaDataExtractor {
  private static final Logger LOG = Logger.getLogger(MetaDataExtractor.class);

  public ImageInfo extract(File image, ImageInfo imageInfo) throws IOException {
    Metadata metadataReader;
    try {
      metadataReader = ImageMetadataReader.readMetadata(image);
    } catch (ImageProcessingException e) {
      throw new IOException(e);
    }

    imageInfo.setFileSize(image.length());

    setGpsInfo(metadataReader, imageInfo); // should be done first to get GPSTime
    setExifInfo(metadataReader, imageInfo);

    if(LOG.isInfoEnabled()) {
      LOG.info(imageInfo.toString());
    }

    return imageInfo;
  }

  private static void setExifInfo(Metadata metadata, ImageInfo meta) {
    OffsetDateTime createDate = deduceCreateDate(metadata, meta);
    meta.setCreateDate(createDate);
    LOG.debug("createDate: "+createDate);

    String artist = MetadataUtil.resolveString(metadata, of(ExifIFD0Directory.class, TAG_ARTIST));
    LOG.debug("artist: "+artist);
    meta.setArtist(artist);

    String cameraMake = MetadataUtil.resolveString(metadata, of(ExifIFD0Directory.class, TAG_MAKE));
    LOG.debug("cameraMake: "+cameraMake);
    meta.setCameraMake(cameraMake);

    String cameraModel = MetadataUtil.resolveString(metadata, of(ExifIFD0Directory.class, TAG_MODEL));
    LOG.debug("cameraModel: "+cameraModel);
    meta.setCameraModel(cameraModel);

    Rational focalLength = resolveRational(metadata, of(ExifSubIFDDirectory.class, TAG_FOCAL_LENGTH));
    LOG.debug("focalLength: "+focalLength);
    if(focalLength != null) {
      meta.setFocalLength(Math.round(focalLength.floatValue()));
    }

    String apertureDescription = MetadataUtil.resolveDescription(metadata, of(ExifSubIFDDirectory.class, TAG_APERTURE));
    LOG.debug("aperture: "+apertureDescription);
    meta.setAperture(apertureDescription);

    Integer isoSpeed = MetadataUtil.resolveInteger(metadata, of(ExifSubIFDDirectory.class, TAG_ISO_EQUIVALENT));
    LOG.debug("isoSpeed: "+isoSpeed);
    meta.setIsoSpeed( isoSpeed );

    Rational shutterSpeed = resolveRational(metadata, of(ExifSubIFDDirectory.class, TAG_EXPOSURE_TIME));
    LOG.debug("shutterSpeed: "+shutterSpeed);
    if (shutterSpeed != null) {
      meta.setShutterSpeedNumerator(shutterSpeed.getNumerator());
      meta.setShutterSpeedDenominator(shutterSpeed.getDenominator());
    }

    Integer imageHeight = MetadataUtil.resolveInteger(metadata, of(ExifSubIFDDirectory.class, TAG_EXIF_IMAGE_HEIGHT));
    LOG.debug("imageHeight: "+imageHeight);
    meta.setImageHeight(imageHeight);

    Integer imageWidth = MetadataUtil.resolveInteger(metadata, of(ExifSubIFDDirectory.class, TAG_EXIF_IMAGE_WIDTH));
    LOG.debug("imageWidth: "+imageWidth);
    meta.setImageWidth(imageWidth);
  }

  /**
   * Use [Google TZ service](https://developers.google.com/maps/documentation/timezone/intro) to
   * derive timezone offset instead of relying on GPS date.
   *
   * @param metadata
   * @param imageInfo
   * @return
   */
  private static OffsetDateTime deduceCreateDate(Metadata metadata, ImageInfo imageInfo) {
    OffsetDateTime createDate = MetadataUtil.resolveDate(metadata, MetadataUtil.createDateTags);

    if(createDate == null) {
      createDate = deduceCreateDateFromFilename(metadata);
    }

    if(createDate == null) {
      LocalDate localDate = imageInfo.getAlbumInfo().getAlbumDate();
      createDate = OffsetDateTime.of(localDate, LocalTime.of(0,0,0), ZoneOffset.UTC);
    }

    OffsetDateTime utcTime = imageInfo.getGpsDatetime();
    if(utcTime != null) {
      ZoneOffset zoneOffset = determineTimeZoneOffset(createDate, utcTime);

      if (zoneOffset != null) {
        createDate = createDate.withOffsetSameLocal(zoneOffset);
      }
    }

    return createDate;
  }

  private static OffsetDateTime deduceCreateDateFromFilename(Metadata metadata) {
    String filename = resolveString(metadata, of(FileMetadataDirectory.class, FileMetadataDirectory.TAG_FILE_NAME));
    if(filename == null || filename.isEmpty()) {
      return null;
    }
    // if the filename looks like this, we can extract from there:
    //    20141118T110523_01.jpg
    String regex = "^(?<date>[0-9]{4}[0-9]{2}[0-9]{2}T[0-9]{2}[0-9]{2}[0-9]{2})";
    Pattern pattern = Pattern.compile(regex);
    Matcher matcher = pattern.matcher(filename);
    boolean success = matcher.find();

    if(!success) {
      return null;
    }

    String date = matcher.group("date");
    DateTimeFormatter format = DateTimeFormatter.ofPattern("yyyyMMdd'T'HHmmss").withZone(ZoneOffset.UTC);
    ZonedDateTime createDate = ZonedDateTime.parse(date, format);
    return createDate.toOffsetDateTime();
  }

  private static void setGpsInfo(Metadata metadata, ImageInfo meta) {
    GpsDirectory dir = (GpsDirectory) getDirectory(metadata, GpsDirectory.class);
    if(dir == null) {
      return;
    }

    Rational altitude = resolveRational(metadata, of(GpsDirectory.class, TAG_ALTITUDE));
    LOG.debug("altitude: "+altitude);
    if(altitude != null) {
      meta.setGpsAlt(altitude.doubleValue());
    }

    OffsetDateTime gpsTime = MetadataUtil.getGpsDate(metadata);
    LOG.debug("gpsTime: "+gpsTime);
    meta.setGpsDatetime( gpsTime );

    GeoLocation loc = dir.getGeoLocation();
    if (loc == null) {
      return;
    }
    LOG.debug("gpsLocation: "+loc.toDMSString());
    meta.setGpsLat( loc.getLatitude() );
    meta.setGpsLon( loc.getLongitude() );
  }
}
