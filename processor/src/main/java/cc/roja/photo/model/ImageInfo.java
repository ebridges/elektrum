package cc.roja.photo.model;

import java.time.LocalDateTime;
import java.time.OffsetDateTime;
import java.util.Objects;
import java.util.UUID;

@SuppressWarnings({"unused"})
public class ImageInfo {

  private UUID owner;
  private String filePath;

  private long fileSize;
  private LocalDateTime createDate;
  private Integer imageWidth;
  private Integer imageHeight;

  private String artist;
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
  private Long focalLengthNumerator;
  private Long focalLengthDenominator;
  private Integer isoSpeed;
  private Double gpsLon;
  private Double gpsLat;
  private Double gpsAlt;
  private OffsetDateTime gpsDateTime;

  public ImageInfo(String filePath) {
    this.filePath = filePath;
  }

  public UUID getOwner() {
    return this.owner;
  }

  public void setOwner(UUID owner) {
    this.owner = owner;
  }

  public String getFilePath() {
    return this.filePath;
  }

  public long getFileSize() {
    return this.fileSize;
  }

  public void setFileSize(long fileSize) {
    this.fileSize = fileSize;
  }

  public LocalDateTime getCreateDate() {
    return this.createDate;
  }

  public void setCreateDate(LocalDateTime createDate) {
    this.createDate = createDate;
  }

  public Integer getImageWidth() {
    return this.imageWidth;
  }

  public void setImageWidth(Integer imageWidth) {
    this.imageWidth = imageWidth;
  }

  public Integer getImageHeight() {
    return this.imageHeight;
  }

  public void setImageHeight(Integer imageHeight) {
    this.imageHeight = imageHeight;
  }

  public String getArtist() {
    return this.artist;
  }

  public void setArtist(String artist) {
    this.artist = artist;
  }

  public String getCameraMake() {
    return this.cameraMake;
  }

  public void setCameraMake(String cameraMake) {
    this.cameraMake = cameraMake;
  }

  public String getCameraModel() {
    return this.cameraModel;
  }

  public void setCameraModel(String cameraModel) {
    this.cameraModel = cameraModel;
  }

  public String getAperture() {
    return this.aperture;
  }

  public void setAperture(String aperture) {
    this.aperture = aperture;
  }

  public Long getShutterSpeedNumerator() {
    return this.shutterSpeedNumerator;
  }

  public void setShutterSpeedNumerator(Long shutterSpeedNumerator) {
    this.shutterSpeedNumerator = shutterSpeedNumerator;
  }

  public Long getShutterSpeedDenominator() {
    return this.shutterSpeedDenominator;
  }

  public void setShutterSpeedDenominator(Long shutterSpeedDenominator) {
    this.shutterSpeedDenominator = shutterSpeedDenominator;
  }

  public Long getFocalLengthNumerator() {
    return this.focalLengthNumerator;
  }

  public void setFocalLengthNumerator(Long focalLengthNumerator) {
    this.focalLengthNumerator = focalLengthNumerator;
  }

  public Long getFocalLengthDenominator() {
    return this.focalLengthDenominator;
  }

  public void setFocalLengthDenominator(Long focalLengthDenominator) {
    this.focalLengthDenominator = focalLengthDenominator;
  }

  public Integer getIsoSpeed() {
    return this.isoSpeed;
  }

  public void setIsoSpeed(Integer isoSpeed) {
    this.isoSpeed = isoSpeed;
  }

  public Double getGpsLon() {
    return this.gpsLon;
  }

  public void setGpsLon(Double gpsLon) {
    this.gpsLon = gpsLon;
  }

  public Double getGpsLat() {
    return this.gpsLat;
  }

  public void setGpsLat(Double gpsLat) {
    this.gpsLat = gpsLat;
  }

  public Double getGpsAlt() {
    return this.gpsAlt;
  }

  public void setGpsAlt(Double gpsAlt) {
    this.gpsAlt = gpsAlt;
  }

  public OffsetDateTime getGpsDateTime() {
    return this.gpsDateTime;
  }

  public void setGpsDateTime(OffsetDateTime gpsDateTime) {
    this.gpsDateTime = gpsDateTime;
  }

  @Override
    public boolean equals(Object o) {
      if (o == this)
        return true;
      if (!(o instanceof ImageInfo)) {
        return false;
      }
      ImageInfo imageInfo = (ImageInfo) o;
      return Objects.equals(owner, imageInfo.owner) 
      && Objects.equals(filePath, imageInfo.filePath) 
      && Objects.equals(mediaType, imageInfo.mediaType) 
      && fileSize == imageInfo.fileSize 
      && Objects.equals(createDate, imageInfo.createDate) 
      && Objects.equals(imageWidth, imageInfo.imageWidth) 
      && Objects.equals(imageHeight, imageInfo.imageHeight) 
      && Objects.equals(artist, imageInfo.artist) 
      && Objects.equals(cameraMake, imageInfo.cameraMake) 
      && Objects.equals(cameraModel, imageInfo.cameraModel) 
      && Objects.equals(aperture, imageInfo.aperture) 
      && Objects.equals(shutterSpeedNumerator, imageInfo.shutterSpeedNumerator) 
      && Objects.equals(shutterSpeedDenominator, imageInfo.shutterSpeedDenominator) 
      && Objects.equals(focalLengthNumerator, imageInfo.focalLengthNumerator) 
      && Objects.equals(focalLengthDenominator, imageInfo.focalLengthDenominator) 
      && Objects.equals(isoSpeed, imageInfo.isoSpeed) 
      && Objects.equals(gpsLon, imageInfo.gpsLon) 
      && Objects.equals(gpsLat, imageInfo.gpsLat) 
      && Objects.equals(gpsAlt, imageInfo.gpsAlt) 
      && Objects.equals(gpsDateTime, imageInfo.gpsDateTime
    );
  }

  @Override
  public int hashCode() {
    return Objects.hash(
      owner, 
      filePath, 
      mediaType, 
      fileSize, 
      createDate, 
      imageWidth, 
      imageHeight, 
      artist, 
      cameraMake, 
      cameraModel, 
      aperture, 
      shutterSpeedNumerator, 
      shutterSpeedDenominator, 
      focalLengthNumerator, 
      focalLengthDenominator, 
      isoSpeed, 
      gpsLon, 
      gpsLat, 
      gpsAlt, 
      gpsDateTime
    );
  }

  @Override
  public String toString() {
    return "{" +
      " owner='" + owner + "'" +
      ", filePath='" + filePath + "'" +
      ", mediaType='" + mediaType + "'" +
      ", fileSize='" + fileSize + "'" +
      ", createDate='" + createDate + "'" +
      ", imageWidth='" + imageWidth + "'" +
      ", imageHeight='" + imageHeight + "'" +
      ", artist='" + artist + "'" +
      ", cameraMake='" + cameraMake + "'" +
      ", cameraModel='" + cameraModel + "'" +
      ", aperture='" + aperture + "'" +
      ", shutterSpeedNumerator='" + shutterSpeedNumerator + "'" +
      ", shutterSpeedDenominator='" + shutterSpeedDenominator + "'" +
      ", focalLengthNumerator='" + focalLengthNumerator + "'" +
      ", focalLengthDenominator='" + focalLengthDenominator + "'" +
      ", isoSpeed='" + isoSpeed + "'" +
      ", gpsLon='" + gpsLon + "'" +
      ", gpsLat='" + gpsLat + "'" +
      ", gpsAlt='" + gpsAlt + "'" +
      ", gpsDatetime='" + gpsDateTime + "'" +
      "}";
  }  
}
