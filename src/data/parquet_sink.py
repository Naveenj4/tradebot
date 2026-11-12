"""
src/data/parquet_sink.py
Asynchronous tick sink writing daily ticks to Apache Parquet files.
Prevents SQLite database bloat and enables fast historical replay.
"""
from pathlib import Path
from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Any
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import logging

logger = logging.getLogger("TradeBot.ParquetSink")

class DailyTickParquetSink:
    def __init__(self, base_directory: str = "./data/ticks"):
        self.base_dir = Path(base_directory)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self._buffer: List[Dict[str, Any]] = []

    def record_tick(self, timestamp: datetime, symbol: str, ltp: Decimal, volume: int = 0) -> None:
        self._buffer.append({
            "timestamp": timestamp,
            "symbol": symbol,
            "ltp": float(ltp),
            "volume": volume
        })

    def flush_to_disk(self, trading_date: str) -> Optional[Path]:
        """Flushes in-memory ticks to {trading_date}.parquet"""
        if not self._buffer:
            logger.info("No ticks buffered to flush.")
            return None

        df = pd.DataFrame(self._buffer)
        output_file = self.base_dir / f"ticks_{trading_date}.parquet"
        
        table = pa.Table.from_pandas(df)
        pq.write_table(table, output_file, compression="SNAPPY")
        
        logger.info(f"Successfully flushed {len(self._buffer)} ticks to {output_file}")
        self._buffer.clear()
        return output_file

