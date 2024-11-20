# Nutrient Flux Project

This notebook is part of a project designed to estimate nutrient flux to Lake Huron as a contribution to the Great Lakes nutrient management efforts.

## Workflow Overview:

The project processes are divided into two environments:

1. **Linux Subsystem**:
   - Used for particle tracking and indirect nutrient estimations.

2. **Windows ArcPy Environment**:
   - Facilitates geospatial analysis and watershed delineation tasks.

## Focus: Direct Nutrient Load

This notebook covers the **direct nutrient load estimation** process, which includes:

### 1. Coastal Watershed Creation:
- **Input Data**:
  - Coastal wetlands shapefiles (from MTRI) representing four main inundation zones.
  - Great Lakes basin streams and D8 flow direction data.
- **Steps**:
  1. Identify and separate streams draining directly to the coastal wetlands.
  2. Use D8 flow direction to delineate watersheds for coastal wetlands.
  3. Remove overlapping regions between coastal and stream watersheds for accuracy.

### 2. Output:
- Watershed shapefiles representing refined coastal watersheds.
- Data ready for further analysis of nutrient loading pathways.

This notebook plays a critical role in supporting the accurate quantification of direct nutrient loads to Lake Huron.

---
