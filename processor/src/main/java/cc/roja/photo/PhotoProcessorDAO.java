package cc.roja.photo;

import java.io.Closeable;

import org.skife.jdbi.v2.sqlobject.Bind;
import org.skife.jdbi.v2.sqlobject.BindBean;
import org.skife.jdbi.v2.sqlobject.SqlQuery;

import cc.roja.photo.util.Constants;

public interface PhotoProcessorDAO extends Closeable {
  @SqlQuery(
      "    with i as (\n"
      + "        insert into collection (name, path)\n"
      + "        select :name, :path\n"
      + "    where not exists (\n"
      + "        select 1\n"
      + "        from collection\n"
      + "        where path = :path\n"
      + "    )\n"
      + "    returning id\n"
      + "    )\n"
      + "    select id from collection where path = :path\n"
      + "    union all\n"
      + "    select id from i\n")
  String getOrCreateCollection(@Bind("name") String name, @Bind("path") String path);

  @SqlQuery(
      "with i as (\n"
      + "      insert into album\n"
      + "          (name, path, album_date, caption, icon, collection_id)\n"
      + "      select\n"
      + "          :a.name, :a.path, :a.albumDate, :a.caption, :a.icon, CAST(:a.collectionId AS UUID)\n"
      + "      where not exists (\n"
      + "          select 1\n"
      + "          from album\n"
      + "          where path = :a.path\n"
      + "      )\n"
      + "      returning id\n"
      + "      )\n"
      + "      select id from album where path = :a.path\n"
      + "      union all\n"
      + "      select id from i")
  String getOrCreateAlbum(@BindBean("a") AlbumInfo albumInfo);

  @SqlQuery(
      "with i as (\n"
      + "        insert into artist (name)\n"
      + "        select :name\n"
      + "        where not exists (\n"
      + "            select 1\n"
      + "            from artist\n"
      + "            where name = :name\n"
      + "        )\n"
      + "        returning id\n"
      + "    )\n"
      + "    select id from artist where name = :name\n"
      + "    union all\n"
      + "    select id from i")
  String getOrCreateArtist(@Bind("name") String artistName);

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
      + "      album_id,\n"
      + "      artist_id,\n"
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
      + "      CAST(:album_id AS UUID),\n"
      + "      CAST(:artist_id AS UUID),\n"
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
  String getOrCreateImage(@Bind("name") String name, @Bind("path") String path, @BindBean("i") ImageInfo imageInfo,
      @Bind("album_id") String albumId, @Bind("artist_id") String artistId);

  @SqlQuery("select id from image where path = :path")
  String queryByPath(@Bind("path") String path);
}
