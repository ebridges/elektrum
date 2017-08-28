package cc.roja.photo;

import java.time.LocalDate;

public class AlbumInfo {
  private String id;
  private String name;
  private String path;
  private String caption;
  private String icon;
  private LocalDate albumDate;
  private String collectionId;

  public AlbumInfo(String name, String path, String caption, String icon, LocalDate albumDate,
      String collectionId) {
    this.name = name;
    this.path = path;
    this.caption = caption;
    this.icon = icon;
    this.albumDate = albumDate;
    this.collectionId = collectionId;
  }

  public String getId() {
    return id;
  }

  public void setId(String id) {
    this.id = id;
  }

  public String getName() {
    return name;
  }

  public String getPath() {
    return path;
  }

  public String getCaption() {
    return caption;
  }

  public String getIcon() {
    return icon;
  }

  public LocalDate getAlbumDate() {
    return albumDate;
  }

  public String getCollectionId() {
    return collectionId;
  }

  @Override
  public String toString() {
    return "AlbumInfo{" +
        "id='" + id + '\'' +
        ", name='" + name + '\'' +
        ", path='" + path + '\'' +
        ", caption='" + caption + '\'' +
        ", icon='" + icon + '\'' +
        ", albumDate=" + albumDate +
        ", collectionId='" + collectionId + '\'' +
        '}';
  }
}
