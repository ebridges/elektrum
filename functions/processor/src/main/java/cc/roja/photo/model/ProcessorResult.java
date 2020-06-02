package cc.roja.photo.model;

import java.util.ArrayList;
import java.util.List;

import com.fasterxml.jackson.annotation.JsonProperty;

public class ProcessorResult {

  @JsonProperty("image_ids")
  private List<String> imageIds;

  public ProcessorResult() {
    this.imageIds = new ArrayList<>();
  }

  @SuppressWarnings("unused")
  public List<String> getImageIds() {
    return imageIds;
  }

  @SuppressWarnings("unused")
  public void setImageIds(List<String> imageIds) {
    this.imageIds = imageIds;
  }

  public int count() {
    return this.imageIds.size();
  }

  @Override
  public String toString() {
    return "ProcessorResult{" +
        "imageId='" + imageIds + '\'' +
        '}';
  }

  public void addImageId(String imageId) {
    if(imageId != null && !imageId.isEmpty()) {
      this.imageIds.add(imageId);
    }
  }
}
