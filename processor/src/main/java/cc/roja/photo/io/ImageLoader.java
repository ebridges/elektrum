package cc.roja.photo.io;

import java.io.File;
import java.io.IOException;

public interface ImageLoader {
  File load(String imageKey) throws IOException;
}
