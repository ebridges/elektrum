package cc.roja.photo.io;

import cc.roja.photo.model.ImageInfo;
import cc.roja.photo.model.ImageKey;

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
      "create_day_id,\n" +
      "file_path,\n" +
      "file_size,\n" +
      "focal_length_denominator,\n" +
      "focal_length_numerator,\n" +
      "gps_alt,\n" +
      "gps_date_time,\n" +
      "gps_lat,\n" +
      "gps_lon,\n" +
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
      ":i.createDayId,\n" +
      ":i.filePath,\n" +
      ":i.fileSize,\n" +
      ":i.focalLengthDenominator,\n" +
      ":i.focalLengthNumerator,\n" +
      ":i.gpsAlt,\n" +
      ":i.gpsDateTime,\n" +
      ":i.gpsLat,\n" +
      ":i.gpsLon,\n" +
      ":i.imageHeight,\n" +
      ":i.imageWidth,\n" +
      ":i.isoSpeed,\n" +
      ":i.mimeType,\n" +
      ":i.shutterSpeed,\n" +
      ":i.shutterSpeedDenominator,\n" +
      ":i.shutterSpeedNumerator) \n" +
    "ON CONFLICT (id) DO UPDATE SET\n" +
      "owner_id = EXCLUDED.owner_id,\n" + 
      "aperture = EXCLUDED.aperture,\n" + 
      "artist = EXCLUDED.artist,\n" + 
      "camera_make = EXCLUDED.camera_make,\n" + 
      "camera_model = EXCLUDED.camera_model,\n" + 
      "create_date = EXCLUDED.create_date,\n" + 
      "create_day_id = EXCLUDED.create_day_id,\n" + 
      "file_path = EXCLUDED.file_path,\n" + 
      "file_size = EXCLUDED.file_size,\n" + 
      "focal_length_denominator = EXCLUDED.focal_length_denominator,\n" + 
      "focal_length_numerator = EXCLUDED.focal_length_numerator,\n" + 
      "gps_alt = EXCLUDED.gps_alt,\n" + 
      "gps_date_time = EXCLUDED.gps_date_time,\n" + 
      "gps_lat = EXCLUDED.gps_lat,\n" + 
      "gps_lon = EXCLUDED.gps_lon,\n" + 
      "image_height = EXCLUDED.image_height,\n" + 
      "image_width = EXCLUDED.image_width,\n" + 
      "iso_speed = EXCLUDED.iso_speed,\n" + 
      "mime_type = EXCLUDED.mime_type,\n" + 
      "shutter_speed = EXCLUDED.shutter_speed,\n" + 
      "shutter_speed_denominator = EXCLUDED.shutter_speed_denominator,\n" + 
      "shutter_speed_numerator = EXCLUDED.shutter_speed_numerator"
 )
    // http://postgis.refractions.net/documentation/manual-1.5SVN/ST_MakePointM.html
  Integer insertImage(@BindBean("i") ImageInfo imageInfo);

  @SqlUpdate("delete from media_item where id = :i.imageId")
  void deleteImage(@BindBean("i") ImageKey imageKey);
}
