package cc.roja.photo.io;

import java.io.Closeable;

import cc.roja.photo.model.ImageInfo;
import cc.roja.photo.model.ImageKey;
import org.skife.jdbi.v2.sqlobject.Bind;
import org.skife.jdbi.v2.sqlobject.BindBean;
import org.skife.jdbi.v2.sqlobject.SqlQuery;

import cc.roja.photo.util.Constants;
import org.skife.jdbi.v2.sqlobject.SqlUpdate;

public interface PhotoProcessorDAO extends Closeable {
  @SqlUpdate(
    "update media_info \n"
  + "set\n"
  + "  file_size = :i.fileSize,\n"
  + "  create_date = :i.createDateTime,\n"
  + "  image_width = :i.imageWidth,\n"
  + "  image_height = :i.imageHeight,\n"
  + "  artist = :i.artist,\n"
  + "  camera_make = :i.cameraMake,\n"
  + "  camera_model = :i.cameraModel,\n"
  + "  aperture = :i.aperture,\n"
  + "  shutter_speed_numerator = :i.shutterSpeedNumerator,\n"
  + "  shutter_speed_denominator = :i.shutterSpeedDenominator,\n"
  + "  shutter_speed = :i.shutterSpeed,\n"
  + "  focal_length_numerator = :i.focalLengthNumerator,\n"
  + "  focal_length_denominator = :i.focalLengthDenominator,\n"
  + "  iso_speed = :i.isoSpeed,\n"
  + "  gps_lon = :i.gpsLon,\n"
  + "  gps_lat = :i.gpsLat,\n"
  + "  gps_alt = :i.gpsAlt,\n"
  + "  gps_date_time = :i.gpsDateTime,\n"
  + "  gps_location = ST_SetSRID(ST_MakePoint(:i.gpsLon, :i.gpsLat, :i.gpsAlt), "+ Constants.SRID+") \n"
  + "where\n"
  + "  file_path = :i.filePath\n"
  + "  and owner = :i.owner\n")
  // http://postgis.refractions.net/documentation/manual-1.5SVN/ST_MakePointM.html
  Integer updateImage(@BindBean("i") ImageInfo imageInfo);

  @SqlQuery("select id from image where file_path = :i.filePath and owner = :i.owner")
  String queryByPath(@Bind("i") ImageKey imageKey);
}
