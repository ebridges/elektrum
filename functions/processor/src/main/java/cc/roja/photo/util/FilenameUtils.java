package cc.roja.photo.util;

/*
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License.  You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

public class FilenameUtils {

  /**
   * The extension separator character.
   */
  private static final char EXTENSION_SEPARATOR = '.';

  /**
   * The Unix separator character.
   */
  private static final char UNIX_SEPARATOR = '/';


  /**
   * Returns the index of the last extension separator character, which is a dot. <p> This method also checks that there
   * is no directory separator after the last dot.
   *
   * @param filename the filename to find the last path separator in, null returns -1
   * @return the index of the last separator character, or -1 if there is no such character
   */
  private static int indexOfExtension(String filename) {
    assert filename != null;
    int extensionPos = filename.lastIndexOf(EXTENSION_SEPARATOR);
    int lastSeparator = filename.lastIndexOf(UNIX_SEPARATOR);
    return (lastSeparator > extensionPos ? -1 : extensionPos);
  }

  /**
   * Gets the extension of a filename. <p> This method returns the textual part of the filename after the last dot.
   * There must be no directory separator after the dot.
   * <pre>
   * foo.txt      --> "txt"
   * a/b/c.jpg    --> "jpg"
   * a/b.txt/c    --> ""
   * a/b/c        --> ""
   * </pre>
   * <p> The output will be the same irrespective of the machine that the code is running on.
   *
   * @param filename the filename to retrieve the extension of.
   * @return the extension of the file or an empty string if none exists.
   */
  public static String getExtension(String filename) {
    if (filename == null) {
      return null;
    }
    int index = indexOfExtension(filename);
    if (index == -1) {
      return "";
    } else {
      return filename.substring(index + 1);
    }
  }
}
