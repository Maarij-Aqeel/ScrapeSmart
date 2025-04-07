import os
import pandas as pd
import streamlit as st
import requests
import io


class DataProcessor:
    """
    Processes and transforms extracted data into structured formats.

    This class provides methods for converting markdown tables to DataFrames,
    processing text data, and other data transformation operations.
    """

    def Result_to_dataframe(self,table):
        """
        Convert a markdown table to a pandas DataFrame.

        Args:
            markdown_table: Markdown-formatted table

        Returns:
            Pandas DataFrame representation of the table
        """
        if not table or "|" not in table:
            return pd.DataFrame()

        lines = table.strip().split("\n")

        # Find header line (should have content and not be separator)
        header_line = None
        for i, line in enumerate(lines):
            if line.strip() and "|" in line and "---" not in line:
                header_line = i
                break

        if header_line is None:
            return pd.DataFrame()

        # Extract header
        header = [h.strip() for h in lines[header_line].strip("|").split("|")]

        table = []
        # Skip header line and separator line
        for line in lines[header_line + 2 :]:
            if not line.strip() or "|" not in line:
                continue

            cols = [col.strip() for col in line.strip("|").split("|")]
            if len(cols) == len(header):
                row = dict(zip(header, cols))
                table.append(row)

        df = pd.DataFrame(table)

        df=df.convert_dtypes(infer_objects=True)

        return df

class FileManager:
        # Maybe Change this
        def save_images(self,path, urls, max_images):
            """
            Download and save images from URLs.

            Args:
                path: Directory path to save images
                urls: List of image URLs to download
                max_images: Maximum number of images to download
            """
            os.makedirs(path, exist_ok=True)
            extension = ""
            headers = {"User-Agent": "Mozilla/5.0"}
            

            for i, url in enumerate(urls, start=1):
                try:
                    response = requests.get(url, headers=headers)

                    if url.endswith(".png"):
                        extension = "png"
                    elif url.endswith(".jpg"):
                        extension = "jpg"

                    elif url.endswith(".jpeg"):
                        extension = "jpeg"

                    elif url.endswith(".svg"):
                        extension = "svg"
                    else:
                        extension = "png"

                    if response.status_code == 200:
                        with open(path + f"image{i}.{extension}", "wb") as file:
                            file.write(response.content)
                    else:
                        st.warning(f"Failed to download image {i}: Status code {response.status_code}")    
                    
                    if i >= max_images:
                        break
                except Exception as e:
                    st.error(f"Error downloading image {i}: {e}")
                    continue

        def save_as(self,df, format_type, file_name):
            """
            Save DataFrame in specified format with streamlit download button.

            Args:
                df: DataFrame to save
                format_type: Format to save (CSV, JSON, XLSX, HTML)
                file_name: Base name for the saved file
            """
            if format_type.upper() == "CSV":
                st.download_button(
                    "Download as CSV",
                    df.to_csv(index=False),
                    file_name=f"{file_name}.csv",
                )
            elif format_type.upper() == "JSON":
                st.download_button(
                    "Download as JSON",
                    df.to_json(orient="records"),
                    file_name=f"{file_name}.json",
                )

            elif format_type.upper() == "XLSX":
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                    df.to_excel(writer, index=False)

                buffer.seek(0)  # Reset pointer to beginning of buffer

                st.download_button(
                    "Download as Excel", data=buffer, file_name=f"{file_name}.xlsx"
                )

            elif format_type.upper() == "HTML":
                st.download_button(
                    "Download as HTML", data=df.to_html(), file_name=f"{file_name}.html"
                )

        def save_text(self,data, file_name):
            """
            Save text content with streamlit download button.

            Args:
                text: Text content to save
                file_name: Base name for the saved file
            """

            st.download_button(
                "Download as plain text", data=data, file_name=f"{file_name}.txt"
            )
