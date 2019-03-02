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
  @SqlQuery(
      "with i as (\n"
      + "    insert into image (\n"
      + "      name,\n"
      + "      path,\n"
      + "      file_size,\n"
      + "      create_date,\n"
      + "      camera_make,\n"
      + "      camera_model,\n"
      + "      aperture,\n"
      + "      shutter_speed_num,\n"
      + "      shutter_speed_den,\n"
      + "      iso_speed,\n"
      + "      focal_length,\n"
      + "      gps_lon,\n"
      + "      gps_lat,\n"
      + "      gps_alt,\n"
      + "      gps_location,\n"
      + "      gps_datetime,\n"
      + "      image_width,\n"
      + "      image_height\n"
      + "    )\n"
      + "    select \n"
      + "      :name,\n"
      + "      :path,\n"
      + "      :i.fileSize,\n"
      + "      :i.createDate,\n"
      + "      :i.cameraMake,\n"
      + "      :i.cameraModel,\n"
      + "      :i.aperture,\n"
      + "      :i.shutterSpeedNumerator,\n"
      + "      :i.shutterSpeedDenominator,\n"
      + "      :i.isoSpeed,\n"
      + "      :i.focalLength,\n"
      + "      :i.gpsLon,\n"
      + "      :i.gpsLat,\n"
      + "      :i.gpsAlt,\n"
      + "      ST_SetSRID(ST_MakePoint(:i.gpsLon, :i.gpsLat, :i.gpsAlt), "+ Constants.SRID+"),\n"
      + "      :i.gpsDatetime,\n"
      + "      :i.imageWidth,\n"
      + "      :i.imageHeight\n"
      + "    where not exists (\n"
      + "        select 1\n"
      + "        from image\n"
      + "        where path = :path\n"
      + "    )\n"
      + "    returning id\n"
      + ")\n"
      + "select id\n"
      + "from image\n"
      + "where path = :path\n"
      + "union all\n"
      + "select id from i")
  // http://postgis.refractions.net/documentation/manual-1.5SVN/ST_MakePointM.html
  String getOrCreateImage(@BindBean("i") ImageInfo imageInfo);

  @SqlUpdate("update media_info set () where id = :imageId")
  void updateImageInfo(String imageId, @BindBean("i") ImageInfo imageInfo);

  @SqlQuery("select id from image where path = :i.filePath and owner = :i.userId")
  String queryByPath(@Bind("i") ImageKey imageKey);
}
