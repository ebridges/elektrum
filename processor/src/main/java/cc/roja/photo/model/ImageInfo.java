package cc.roja.photo.model;

import java.time.LocalDateTime;
import java.time.OffsetDateTime;

@SuppressWarnings({"unused"})
public class ImageInfo {

  private String artist;
  private long fileSize;
  private LocalDateTime createDate;
  private String cameraMake;
  private String cameraModel;
  /**
   * The actual aperture value of lens when the image was taken. Unit is APEX.
   * To convert this value to ordinary F-number (F-stop), calculate this value's
   * power of root 2 (=1.4142). For example, if the ApertureValue is '5',
   * F-number is 1.4142^5 = F5.6.
   * https://photo.stackexchange.com/a/60950/1789
   */
  private String aperture;
  private Long shutterSpeedNumerator;
  private Long shutterSpeedDenominator;
  private Integer isoSpeed;
  private Double gpsLon;
  private Double gpsLat;
  private Double gpsAlt;
  private OffsetDateTime gpsDatetime;
  private Integer imageWidth;
  private Integer imageHeight;
  private Long focalLengthNumerator;
  private Long focalLengthDenominator;

  public ImageInfo() {
  }

  public Integer getImageWidth() {
    return imageWidth;
  }

  public void setImageWidth(Integer imageWidth) {
    this.imageWidth = imageWidth;
  }

  public Integer getImageHeight() {
    return imageHeight;
  }

  public void setImageHeight(Integer imageHeight) {
    this.imageHeight = imageHeight;
  }

  public String getArtist() {
    return artist;
  }

  public void setArtist(String artist) {
    this.artist = artist;
  }

  public long getFileSize() {
    return fileSize;
  }

  public void setFileSize(long fileSize) {
    this.fileSize = fileSize;
  }

  public LocalDateTime getCreateDate() {
    return createDate;
  }

  public void setCreateDate(LocalDateTime createDate) {
    this.createDate = createDate;
  }

  public String getCameraMake() {
    return cameraMake;
  }

  public void setCameraMake(String cameraMake) {
    this.cameraMake = cameraMake;
  }

  public String getAperture() {
    return aperture;
  }

  public void setAperture(String aperture) {
    this.aperture = aperture;
  }

  public Integer getIsoSpeed() {
    return isoSpeed;
  }

  public void setIsoSpeed(Integer isoSpeed) {
    this.isoSpeed = isoSpeed;
  }

  public void setFocalLengthNumerator(long focalLengthNumerator) {
    this.focalLengthNumerator = focalLengthNumerator;
  }

  public long getFocalLengthNumerator() {
    return focalLengthNumerator;
  }

  public void setFocalLengthDenominator(long focalLengthDenominator) {
    this.focalLengthDenominator = focalLengthDenominator;
  }

  public long getFocalLengthDenominator() {
    return focalLengthDenominator;
  }

  public Double getGpsLon() {
    return gpsLon;
  }

  public void setGpsLon(Double gpsLon) {
    this.gpsLon = gpsLon;
  }

  public Double getGpsLat() {
    return gpsLat;
  }

  public void setGpsLat(Double gpsLat) {
    this.gpsLat = gpsLat;
  }

  public void setGpsAlt(Double gpsAlt) {
    this.gpsAlt = gpsAlt;
  }

  public Double getGpsAlt() {
    return gpsAlt;
  }

  public OffsetDateTime getGpsDatetime() {
    return gpsDatetime;
  }

  public void setGpsDatetime(OffsetDateTime gpsDatetime) {
    this.gpsDatetime = gpsDatetime;
  }

  public String getCameraModel() {
    return cameraModel;
  }

  public void setCameraModel(String cameraModel) {
    this.cameraModel = cameraModel;
  }

  public Long getShutterSpeedNumerator() {
    return shutterSpeedNumerator;
  }

  public void setShutterSpeedNumerator(Long shutterSpeedNumerator) {
    this.shutterSpeedNumerator = shutterSpeedNumerator;
  }

  public Long getShutterSpeedDenominator() {
    return shutterSpeedDenominator;
  }

  public void setShutterSpeedDenominator(Long shutterSpeedDenominator) {
    this.shutterSpeedDenominator = shutterSpeedDenominator;
  }

  @Override
  public String toString() {
    return "ImageInfo{" +
        "artist='" + artist + '\'' +
        ", fileSize=" + fileSize +
        ", createDate=" + createDate +
        ", cameraMake='" + cameraMake + '\'' +
        ", cameraModel='" + cameraModel + '\'' +
        ", aperture='" + aperture + '\'' +
        ", shutterSpeedNumerator=" + shutterSpeedNumerator +
        ", shutterSpeedDenominator=" + shutterSpeedDenominator +
        ", isoSpeed=" + isoSpeed +
        ", gpsLon=" + gpsLon +
        ", gpsLat=" + gpsLat +
        ", gpsAlt=" + gpsAlt +
        ", gpsDatetime=" + gpsDatetime +
        ", imageWidth=" + imageWidth +
        ", imageHeight=" + imageHeight +
        ", focalLengthNumerator=" + focalLengthNumerator +
        ", focalLengthDenominator=" + focalLengthDenominator +
        '}';
  }
}
