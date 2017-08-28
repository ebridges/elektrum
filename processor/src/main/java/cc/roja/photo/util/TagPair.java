package cc.roja.photo.util;

import com.drew.metadata.Directory;

@SuppressWarnings("WeakerAccess")
public class TagPair {
  public final Class<? extends Directory>  directory;
  public final Integer tag;

  private TagPair(Class<? extends Directory>  directory, Integer tag) {
    this.directory = directory;
    this.tag = tag;
  }

  public static TagPair of(Class<? extends Directory> directory, Integer tag) {
    return new TagPair(directory, tag);
  }

  @Override
  public String toString() {
    return "{" +
        "directory=" + directory.getSimpleName() +
        ", tag=" + tag + " ("+String.format("0x%08X", tag)+")" +
        '}';
  }
}
