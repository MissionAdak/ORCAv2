import * as SQLite from 'expo-sqlite';

let dbPromise: Promise<SQLite.SQLiteDatabase> | null = null;

async function getDB() {
  if (!dbPromise) {
    dbPromise = SQLite.openDatabaseAsync('orca_offline.db');
  }

  const db = await dbPromise;

  await db.execAsync(`
    PRAGMA journal_mode = WAL;

    CREATE TABLE IF NOT EXISTS cache (
      key TEXT PRIMARY KEY NOT NULL,
      payload TEXT NOT NULL,
      updated_at INTEGER NOT NULL
    );

    CREATE TABLE IF NOT EXISTS sos_queue (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      client_uuid TEXT UNIQUE NOT NULL,
      payload TEXT NOT NULL,
      created_at INTEGER NOT NULL,
      status TEXT NOT NULL DEFAULT 'pending',
      attempts INTEGER NOT NULL DEFAULT 0
    );
  `);

  return db;
}

export async function cacheData(
  key: string,
  payload: unknown
) {
  const db = await getDB();

  await db.runAsync(
    `INSERT OR REPLACE INTO cache
     (key, payload, updated_at)
     VALUES (?, ?, ?)`,
    key,
    JSON.stringify(payload),
    Date.now()
  );
}

export async function getCachedData<T>(
  key: string
): Promise<{
  data: T;
  updatedAt: number;
} | null> {
  const db = await getDB();

  const row = await db.getFirstAsync<{
    payload: string;
    updated_at: number;
  }>(
    `SELECT payload, updated_at
     FROM cache
     WHERE key = ?`,
    key
  );

  if (!row) {
    return null;
  }

  return {
    data: JSON.parse(row.payload) as T,
    updatedAt: row.updated_at,
  };
}

export async function queueSOS(
  clientUuid: string,
  payload: unknown
) {
  const db = await getDB();

  await db.runAsync(
    `INSERT OR IGNORE INTO sos_queue
     (client_uuid, payload, created_at, status, attempts)
     VALUES (?, ?, ?, 'pending', 0)`,
    clientUuid,
    JSON.stringify(payload),
    Date.now()
  );
}

export async function getPendingSOS() {
  const db = await getDB();

  return db.getAllAsync<{
    id: number;
    client_uuid: string;
    payload: string;
    created_at: number;
    status: string;
    attempts: number;
  }>(
    `SELECT *
     FROM sos_queue
     WHERE status = 'pending'
     ORDER BY created_at ASC`
  );
}

export async function markSOSSynced(id: number) {
  const db = await getDB();

  await db.runAsync(
    `DELETE FROM sos_queue WHERE id = ?`,
    id
  );
}

export async function incrementSOSAttempt(id: number) {
  const db = await getDB();

  await db.runAsync(
    `UPDATE sos_queue
     SET attempts = attempts + 1
     WHERE id = ?`,
    id
  );
}

export async function getPendingSOSCount() {
  const db = await getDB();

  const row = await db.getFirstAsync<{
    count: number;
  }>(
    `SELECT COUNT(*) as count
     FROM sos_queue
     WHERE status = 'pending'`
  );

  return row?.count ?? 0;
}