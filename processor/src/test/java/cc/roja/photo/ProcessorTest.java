package cc.roja.photo;

import cc.roja.photo.io.ImageLoader;
import cc.roja.photo.io.PhotoProcessorDAO;
import cc.roja.photo.metadata.MetaDataExtractor;
import cc.roja.photo.model.ImageInfo;
import cc.roja.photo.model.ImageKey;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.skife.jdbi.v2.DBI;

import java.io.File;
import java.io.IOException;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

class ProcessorTest {
  private DBI mockDbi;
  private ImageLoader mockImageLoader;
  private MetaDataExtractor mockMetaDataExtractor;
  private PhotoProcessorDAO mockDao;

  @BeforeEach
  void setup() {
    this.mockDbi = mock(DBI.class);
    this.mockImageLoader = mock(ImageLoader.class);
    this.mockMetaDataExtractor = mock(MetaDataExtractor.class);
    this.mockDao = mock(PhotoProcessorDAO.class);
    when(this.mockDbi.open(PhotoProcessorDAO.class)).thenReturn(this.mockDao);
  }

  @Test
  void testProcessPhoto_Success() throws IOException {
    Processor underTest = new Processor(this.mockDbi, this.mockImageLoader, this.mockMetaDataExtractor);
    String expectedImageId = "abcd";

    ImageKey mockImageKey = mock(ImageKey.class);
    when(mockImageKey.getFilePath()).thenReturn("defg");
    File mockFile = mock(File.class);
    ImageInfo imageInfo = new ImageInfo(mockImageKey.getFilePath());

    when(this.mockDao.queryByPath(mockImageKey)).thenReturn(expectedImageId);
    when(this.mockImageLoader.load(mockImageKey.getKey())).thenReturn(mockFile);
    when(this.mockMetaDataExtractor.extract(mockImageKey, mockFile)).thenReturn(imageInfo);

    String actualImageId = underTest.processPhoto(mockImageKey);

    assertEquals(expectedImageId, actualImageId);
  }

  @Test
  void testProcessPhoto_NoRecordForImageKey() {
    Processor underTest = new Processor(this.mockDbi, this.mockImageLoader, this.mockMetaDataExtractor);
    ImageKey imageKey = new ImageKey();
    when(this.mockDao.queryByPath(imageKey)).thenReturn(null);
    assertThrows(IllegalArgumentException.class, () -> underTest.processPhoto(imageKey));
  }
}