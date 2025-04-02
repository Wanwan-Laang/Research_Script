Sure! Here’s a complete Markdown (.md) version of the documentation written in formal scientific English:

⸻



# Adsorption Site Generator for High-Entropy Ceramics (HECs)

This script is designed to identify and construct **three classes of adsorption sites**—**ontop**, **bridge**, and **hollow**—on the surface of a high-entropy ceramic (HEC) slab. It outputs labeled structures and a visual preview for each adsorption category. The primary goal is to automate the setup of surface adsorption configurations for use in first-principles calculations (e.g., VASP).

---

## 🧠 Conceptual Rationale

### 1. Identifying the Top Surface Layer

- The adsorption process typically occurs on the topmost layer of the slab.
- This script identifies surface atoms as those whose z-coordinates fall within 1 Å of the maximum value (`z_highest`), i.e.:

z_lowest = z_highest - 1.0 Å

- This approach is robust to minor surface roughness due to relaxation and is particularly well-suited for **low-symmetry or disordered systems** like HECs.

### 2. Ontop Sites

- For each atom in the surface layer, an adsorption site is generated directly above its \((x, y)\) coordinate.
- The adsorption height is defined as:

z_set = z_highest + 2.0 Å

- This results in a typical **ontop configuration**:  
> Adsorbate is vertically aligned above a single substrate atom.

### 3. Bridge Sites

- **Nearest-neighbor atom pairs** within the surface layer are identified using `ASE`'s neighbor list (with a 3.0 Å cutoff).
- For each pair, the midpoint between their \((x, y)\) coordinates is used to construct the bridge site.

### 4. Hollow Sites (Rectangle-Based)

- Traditional hollow sites are based on equilateral triangles (e.g., fcc or hcp sites).
- For **HECs and other low-symmetry materials**, triangle-based hollows often lead to degenerate, redundant, or unrealistic sites.
- This script instead uses a **four-atom cluster** strategy:
- Groups of four surface atoms are selected if all pairwise distances fall within a reasonable geometric range (1.0–3.2 Å).
- The centroid of these atoms defines the hollow adsorption site.
- **Redundancy filtering** ensures that duplicate or closely packed sites are removed.

---

## 📂 Outputs

### 1. Structural Files

Three directories will be generated:

- `adsorption_ontop/`
- `adsorption_bridge/`
- `adsorption_hollow/`

Each folder contains POSCAR files with a hydrogen atom placed at each identified adsorption site.

### 2. Preview Plot

- A PNG image (`adsorption_sites_preview.png`) will visualize the top-layer atoms and adsorption positions.
- The plot uses distinct colors for each category:
- Green for ontop
- Red for bridge
- Blue for hollow

### 3. Console Summary

- The script prints the total number of adsorption sites for each category.

---

## 🧪 Applications

This workflow is especially suitable for:

- High-throughput adsorption energy screening
- Systems with broken symmetry (e.g., defects, doped surfaces, HEC/HEA)
- Surfaces after geometry relaxation

---

## 🛠️ Further Extensions

To build more complex adsorption systems (e.g., multi-atom adsorbates, varied orientations, surface reconstructions), this script can be extended using:

- `ASE` for adsorbate rotation and constraints
- `pymatgen` for symmetry and bonding analysis
- `CatKit` for advanced site classification

---

**Author**:  
*Generated with the assistance of ChatGPT and ASE/Pymatgen tools.*  
*Date: April 2025*

Let me know if you’d like me to save this as a .md file or include the script inline as a code block too.