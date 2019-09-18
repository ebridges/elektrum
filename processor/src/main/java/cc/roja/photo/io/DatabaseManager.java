package cc.roja.photo.io;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.jdbi.v3.core.Jdbi;
import org.jdbi.v3.sqlobject.SqlObjectPlugin;
import org.postgresql.ds.PGSimpleDataSource;

public class DatabaseManager {
  private static final Logger LOG = LogManager.getLogger(DatabaseManager.class);

  public static Jdbi getDBI() {
    Jdbi jdbi = null;
    // When using sqlite (in test mode), username is not used
    if(System.getenv("DB_USERNAME") == null) {
      jdbi = sqliteDBI();
    } else {
      jdbi = postgresqlDBI();
    }
    jdbi.installPlugin(new SqlObjectPlugin());
    return jdbi;
  }

  private static Jdbi postgresqlDBI() {
    LOG.info("postgresqlDBI called with URL: {}", System.getenv("DB_JDBC_URL"));
    PGSimpleDataSource dataSource = new PGSimpleDataSource();
    String jdbc_url = System.getenv("DB_JDBC_URL");
    String username = System.getenv("DB_USERNAME");
    String password = System.getenv("DB_PASSWORD");

    dataSource.setUrl(jdbc_url);
    dataSource.setUser(username);
    dataSource.setPassword(password);
    dataSource.setApplicationName("photo-processor");
    // source.setSocketTimeout(); default is "0" which means disable timeout on
    // connection reads

    return Jdbi.create(dataSource);
  }

  private static Jdbi sqliteDBI() {
    LOG.info("sqliteDBI called with URL: {}", System.getenv("DB_JDBC_URL"));
    String jdbcUrl = System.getenv("DB_JDBC_URL");
    Connection conn;
    try {
      conn = DriverManager.getConnection(jdbcUrl);
    } catch (SQLException e) {
      throw new IllegalStateException(e);
    }
    return Jdbi.create(conn);
  }
}
