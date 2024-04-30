# """
# 提取数据的一些工具类
# """
# import pdfplumber
#
# from pathlib import Path
# from typing import (Union, Optional, List, Dict)
#
#
# def extract_table_f_pdfs(file_path: Union[str, Path]) -> Optional[Dict[int, List]]:
#     """
#     提取pdf文件中的表格
#     """
#     data = {}
#     file_path = Path(file_path)
#     if file_path.exists():
#         pdf = pdfplumber.open(file_path)
#         for page in pdf.pages:
#             table = page.extract_table()
#             if table is not None:
#                 data[page.page_number] = page.extract_table()
#         return data
