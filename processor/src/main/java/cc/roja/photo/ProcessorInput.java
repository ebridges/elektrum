package cc.roja.photo;

import com.fasterxml.jackson.annotation.JsonProperty;

public class ProcessorInput {

  @JsonProperty("image_key")
  private String imageKey;

  public String getImageKey() {
    return imageKey;
  }

  public void setImageKey(String imageKey) {
    this.imageKey = imageKey;
  }
}
