package cc.roja.photo.io;

import cc.roja.photo.model.ImageInfo;

import cc.roja.photo.util.Constants;
import org.jdbi.v3.sqlobject.customizer.BindBean;
import org.jdbi.v3.sqlobject.statement.SqlUpdate;

public interface PhotoProcessorDAO {


  @SqlUpdate("insert into media_item (" +
      "id,\n" +
      "owner_id,\n" +
      "aperture,\n" +
      "artist,\n" +
      "camera_make,\n" +
      "camera_model,\n" +
      "create_date,\n" +
      "file_path,\n" +
      "file_size,\n" +
      "focal_length_denominator,\n" +
      "focal_length_numerator,\n" +
      "gps_alt,\n" +
      "gps_date_time,\n" +
      "gps_lat,\n" +
      "gps_lon,\n" +
      "gps_location,\n" +
      "image_height,\n" +
      "image_width,\n" +
      "iso_speed,\n" +
      "mime_type,\n" +
      "shutter_speed,\n" +
      "shutter_speed_denominator,\n" +
      "shutter_speed_numerator\n" +
   ") values (" +
      ":i.id,\n" +
      ":i.owner,\n" +
      ":i.aperture,\n" +
      ":i.artist,\n" +
      ":i.cameraMake,\n" +
      ":i.cameraModel,\n" +
      ":i.createDateTime,\n" +
      ":i.filePath,\n" +
      ":i.fileSize,\n" +
      ":i.focalLengthDenominator,\n" +
      ":i.focalLengthNumerator,\n" +
      ":i.gpsAlt,\n" +
      ":i.gpsDateTime,\n" +
      ":i.gpsLat,\n" +
      ":i.gpsLon,\n" +
      "ST_SetSRID(ST_MakePoint(:i.gpsLon, :i.gpsLat, :i.gpsAlt), "+ Constants.SRID+"),\n" +
      ":i.imageHeight,\n" +
      ":i.imageWidth,\n" +
      ":i.isoSpeed,\n" +
      ":i.mimeType,\n" +
      ":i.shutterSpeed,\n" +
      ":i.shutterSpeedDenominator,\n" +
      ":i.shutterSpeedNumerator\n" +
   ")")
    // http://postgis.refractions.net/documentation/manual-1.5SVN/ST_MakePointM.html
  Integer insertImage(@BindBean("i") ImageInfo imageInfo);
}
