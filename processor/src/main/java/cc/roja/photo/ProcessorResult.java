package cc.roja.photo;

import com.fasterxml.jackson.annotation.JsonProperty;

@SuppressWarnings({"WeakerAccess", "unused"})
public class ProcessorResult {

  @JsonProperty("image_id")
  private String imageId;

  public String getImageId() {
    return imageId;
  }

  public void setImageId(String imageId) {
    this.imageId = imageId;
  }

  @Override
  public String toString() {
    return "ProcessorResult{" +
        "imageId='" + imageId + '\'' +
        '}';
  }
}
