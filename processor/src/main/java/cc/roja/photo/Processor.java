package cc.roja.photo;

import java.io.File;
import java.io.IOException;

import cc.roja.photo.io.DatabaseManager;
import cc.roja.photo.io.ImageLoader;
import cc.roja.photo.io.ImageLoaderFactory;
import cc.roja.photo.io.PhotoProcessorDAO;
import cc.roja.photo.metadata.MetaDataExtractor;
import cc.roja.photo.model.ImageInfo;
import cc.roja.photo.model.ImageKey;
import org.skife.jdbi.v2.DBI;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import static java.lang.String.format;

@SuppressWarnings({"unused","WeakerAccess"})
public class Processor {
  private static final Logger LOG = LogManager.getLogger(Processor.class);

  private DBI dbi;
  private ImageLoader imageLoader;
  private MetaDataExtractor metaDataExtractor;

  public Processor(DBI dbi, ImageLoader imageLoader, MetaDataExtractor metaDataExtractor) {
    this.dbi = dbi;
    this.imageLoader = imageLoader;
    this.metaDataExtractor = metaDataExtractor;
  }

  public Processor() {
    this(DatabaseManager.getDBI(), ImageLoaderFactory.getLoader(), new MetaDataExtractor());
  }

  public String processPhoto(ImageKey imageKey) throws IOException {
    try (PhotoProcessorDAO dao = dbi.open(PhotoProcessorDAO.class)) {
      String imageId = dao.queryByPath(imageKey);

      if(imageId == null) {
        LOG.warn(format("No image record found for: [%s]", imageKey));
        throw new IllegalArgumentException(format("No image record found for: [%s]", imageKey));
      }

      LOG.info("Processing: " + imageKey);

      // identify a filesystem location for the media item, which will mean a network op for S3
      File imageFile = imageLoader.load(imageKey.getKey());

      // extract and normalize metadata from the media file
      ImageInfo imageInfo = metaDataExtractor.extract(imageKey, imageFile);

      // store the metadata linked to the media id record
      dao.updateImageInfo(imageId, imageInfo);

      return imageId;
    }
  }
}
