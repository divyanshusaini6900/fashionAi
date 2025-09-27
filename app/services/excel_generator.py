import pandas as pd
from typing import Dict, Any, List, Optional
import io
from app.core.config import settings
import os
import logging

# Configure logging
logger = logging.getLogger(__name__)

class ExcelGenerator:
    def __init__(self, template_path: str = None):
        """Initialize the Excel generator with an optional template."""
        self.template_path = template_path
        try:
            if self.template_path and os.path.exists(self.template_path):
                logger.info(f"Loading Excel template from {template_path}")
                self.template_df = pd.read_excel(template_path)
            else:
                logger.info("No template found, creating default structure")
                self.template_df = pd.DataFrame({
                    "SKU_ID": [],
                    "Description": [],
                    "Key Features": [],
                    "Search Keywords": [],
                    "Front View URL": [],
                    "Side View URL": [],
                    "Back View URL": [],
                    "Video URL": []
                })
        except Exception as e:
            logger.error(f"Error initializing Excel generator: {str(e)}")
            raise

    def _prepare_data(self, product_data: Dict[str, Any], variation_urls: Optional[Dict[str, str]] = None, video_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Prepares the detailed product data for Excel, ensuring all values are serializable.
        
        Args:
            product_data: The structured product data
            variation_urls: Optional dictionary of view names to image URLs for variations.
            video_url: Optional URL for the generated video
        """
        try:
            logger.info("Preparing data for Excel report")
            logger.info(f"Product data keys: {list(product_data.keys())}")
            logger.info(f"Number of variations: {len(variation_urls) if variation_urls else 0}")

            # Make a copy to avoid modifying the original dict
            data = {
                "SKU_ID": product_data.get("SKU_ID"),
                "Description": product_data.get("Description"),
            }
            
            # Define allowed view types for columns (excluding detail views)
            allowed_views = {'frontside', 'backside', 'sideview'}
            view_name_mapping = {
                'frontside': 'Front View URL',
                'backside': 'Back View URL', 
                'sideview': 'Side View URL'
            }
            
            # Add variation URLs if provided, only for allowed views
            if variation_urls:
                for view_name, url in variation_urls.items():
                    # Only create columns for front, back, and side views (not detail views)
                    if view_name.lower() in allowed_views:
                        column_name = view_name_mapping.get(view_name.lower(), f"{view_name.replace('_', ' ').title()} View URL")
                        data[column_name] = url
                        logger.info(f"Added {column_name}: {url}")
                    else:
                        logger.info(f"Skipping column creation for view: {view_name} (detail view excluded)")

            # Add video URL
            data["Video URL"] = video_url if video_url else ""

            # Handle special fields
            if "Search Keywords" in product_data and isinstance(product_data["Search Keywords"], list):
                data["Search Keywords"] = ", ".join(product_data["Search Keywords"])
            
            if "Key Features" in product_data and isinstance(product_data["Key Features"], list):
                data["Key Features"] = "\n".join([f"• {feature}" for feature in product_data["Key Features"]])

            # Convert any remaining list values to comma-separated strings
            for key, value in data.items():
                if isinstance(value, list):
                    data[key] = ", ".join(map(str, value))
                elif value in [None, "", "Not Specified", "Not Visible"]:
                    if key in ["Description", "Key Features"]:
                        data[key] = "Product details to be added"
                    else:
                        data[key] = "To be specified"
            
            # Ensure all template columns are present in the data
            view_columns = ["Front View URL", "Side View URL", "Back View URL"]
            for column in self.template_df.columns:
                if column not in data:
                    # For view columns, only add them if they're supposed to have data
                    # Otherwise, leave them empty instead of "To be specified"
                    if column in view_columns:
                        data[column] = ""  # Empty string for view columns without data
                    else:
                        data[column] = "To be specified"  # Default for other columns
            
            logger.info(f"Final data keys: {list(data.keys())}")
            return data

        except Exception as e:
            logger.error(f"Error preparing Excel data: {str(e)}")
            raise

    def create_report(self, product_data: Dict[str, Any], variation_urls: Optional[Dict[str, str]] = None, video_url: Optional[str] = None) -> bytes:
        """
        Creates a detailed Excel report from the rich product data dictionary.
        
        Args:
            product_data: The structured product data from the workflow.
            variation_urls: Optional dictionary of view names to image URLs for variations.
            video_url: Optional URL for the generated video.
            
        Returns:
            The Excel file as bytes.
        """
        try:
            logger.info("Starting Excel report creation")
            
            # Validate inputs
            if not isinstance(product_data, dict):
                raise ValueError(f"product_data must be a dictionary, got {type(product_data)}")
            
            # Prepare the data, converting lists to strings and adding the image URLs
            prepared_data = self._prepare_data(product_data, variation_urls, video_url)
            
            # Create a DataFrame from the dictionary
            logger.info("Creating DataFrame from prepared data")
            report_df = pd.DataFrame([prepared_data])  # Wrap in list to ensure single row
            
            # Determine the column order with proper view URL positioning
            static_columns = list(self.template_df.columns)
            
            # Define the preferred order for view columns
            preferred_view_order = ["Front View URL", "Side View URL", "Back View URL"]
            
            # Extract dynamically generated variation columns that are actually present in the data
            variation_columns = []
            for view_col in preferred_view_order:
                if view_col in prepared_data:
                    variation_columns.append(view_col)
            
            # Add any other view columns not in the preferred order
            other_view_columns = sorted([
                col for col in prepared_data.keys() 
                if col.endswith(" View URL") and col not in variation_columns
            ])
            variation_columns.extend(other_view_columns)
            
            # Position variation columns after Search Keywords (before Video URL)
            try:
                keywords_index = static_columns.index("Search Keywords")
                # Remove any pre-defined view columns from static columns that are in variation_columns
                filtered_static_columns = [col for col in static_columns if col not in variation_columns]
                keywords_index = filtered_static_columns.index("Search Keywords")
                final_columns = (
                    filtered_static_columns[:keywords_index + 1] +
                    variation_columns +
                    filtered_static_columns[keywords_index + 1:]
                )
            except ValueError:
                # Fallback - put view columns before video URL
                final_columns = [col for col in static_columns if col not in variation_columns]
                if "Video URL" in final_columns:
                    video_index = final_columns.index("Video URL")
                    final_columns = final_columns[:video_index] + variation_columns + final_columns[video_index:]
                else:
                    final_columns.extend(variation_columns)

            # Ensure all columns from the report are included in the final list
            for col in report_df.columns:
                if col not in final_columns:
                    final_columns.append(col)

            # Reorder columns to match the desired layout
            report_df = report_df.reindex(columns=final_columns)
            
            # Write the DataFrame to an in-memory buffer
            logger.info("Writing DataFrame to Excel buffer")
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                report_df.to_excel(writer, sheet_name='Product_Details', index=False)
            
            logger.info("Excel report created successfully")
            # Retrieve the bytes from the buffer
            return output.getvalue()

        except Exception as e:
            logger.error(f"Error creating Excel report: {str(e)}")
            raise
