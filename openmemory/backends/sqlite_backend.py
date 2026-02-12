"""SQLite backend for long-term memory"""

import json
import sqlite3
from typing import List, Dict, Optional
from datetime import datetime

from ..core.memory import Memory


class SQLiteBackend:
    """SQLite backend for persistent memory storage"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                user_id TEXT,
                agent_id TEXT,
                session_id TEXT,
                category TEXT DEFAULT 'general',
                importance REAL DEFAULT 0.5,
                created_at TEXT,
                updated_at TEXT,
                metadata TEXT
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user ON memories(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_category ON memories(category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_session ON memories(session_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_created ON memories(created_at)")
        
        conn.commit()
        conn.close()
    
    def add(self, memory: Memory):
        """Add a memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO memories 
            (id, content, user_id, agent_id, session_id, category, importance, created_at, updated_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            memory.id,
            memory.content,
            memory.user_id,
            memory.agent_id,
            memory.session_id,
            memory.category,
            memory.importance,
            memory.created_at,
            memory.updated_at,
            json.dumps(memory.metadata)
        ))
        
        conn.commit()
        conn.close()
    
    def get(self, memory_id: str) -> Optional[Memory]:
        """Get memory by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM memories WHERE id = ?", (memory_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self._row_to_memory(row)
        return None
    
    def update(self, memory: Memory):
        """Update a memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE memories 
            SET content = ?, importance = ?, updated_at = ?, metadata = ?
            WHERE id = ?
        """, (
            memory.content,
            memory.importance,
            memory.updated_at,
            json.dumps(memory.metadata),
            memory.id
        ))
        
        conn.commit()
        conn.close()
    
    def delete(self, memory_id: str) -> int:
        """Delete memory by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
        deleted = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return deleted
    
    def delete_by_filters(self, filters: Dict) -> int:
        """Delete memories matching filters"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        conditions = []
        values = []
        
        for key, value in filters.items():
            conditions.append(f"{key} = ?")
            values.append(value)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        cursor.execute(f"DELETE FROM memories WHERE {where_clause}", values)
        deleted = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return deleted
    
    def search(
        self,
        query: str,
        user_id: str = None,
        category: str = None,
        limit: int = 10
    ) -> List[Dict]:
        """Search memories by keyword"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        conditions = ["content LIKE ?"]
        values = [f"%{query}%"]
        
        if user_id:
            conditions.append("user_id = ?")
            values.append(user_id)
        
        if category:
            conditions.append("category = ?")
            values.append(category)
        
        where_clause = " AND ".join(conditions)
        
        cursor.execute(f"""
            SELECT * FROM memories 
            WHERE {where_clause}
            ORDER BY importance DESC, updated_at DESC
            LIMIT ?
        """, values + [limit])
        
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_dict(row) for row in rows]
    
    def get_recent(
        self,
        user_id: str,
        session_id: str = None,
        limit: int = 20
    ) -> List[Memory]:
        """Get recent memories"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if session_id:
            cursor.execute("""
                SELECT * FROM memories 
                WHERE user_id = ? AND (session_id = ? OR session_id IS NULL)
                ORDER BY updated_at DESC
                LIMIT ?
            """, (user_id, session_id, limit))
        else:
            cursor.execute("""
                SELECT * FROM memories 
                WHERE user_id = ?
                ORDER BY updated_at DESC
                LIMIT ?
            """, (user_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_memory(row) for row in rows]
    
    def get_by_category(
        self,
        user_id: str,
        category: str,
        min_importance: float = 0.0,
        limit: int = 10
    ) -> List[Memory]:
        """Get memories by category"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM memories 
            WHERE user_id = ? AND category = ? AND importance >= ?
            ORDER BY importance DESC, updated_at DESC
            LIMIT ?
        """, (user_id, category, min_importance, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_memory(row) for row in rows]
    
    def _row_to_memory(self, row) -> Memory:
        """Convert DB row to Memory object"""
        return Memory(
            id=row[0],
            content=row[1],
            user_id=row[2],
            agent_id=row[3],
            session_id=row[4],
            category=row[5],
            importance=row[6],
            created_at=row[7],
            updated_at=row[8],
            metadata=json.loads(row[9]) if row[9] else {}
        )
    
    def _row_to_dict(self, row) -> Dict:
        """Convert DB row to dict"""
        return {
            "id": row[0],
            "content": row[1],
            "user_id": row[2],
            "agent_id": row[3],
            "session_id": row[4],
            "category": row[5],
            "importance": row[6],
            "created_at": row[7],
            "updated_at": row[8],
            "metadata": json.loads(row[9]) if row[9] else {}
        }
