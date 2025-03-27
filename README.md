# NEVERLATEX: Real-Time Handwriting Recognition with Sensor-Equipped Pen ✍️

This project presents a low-cost, sensor-driven handwriting recognition system capable of converting handwritten input into digital text in real-time. The system uses a custom-built pen integrated with IMU and force sensors, alongside a CLDNN deep learning architecture and CTC decoding for accurate recognition.

---

## 📁 Project Structure

```
NEVERLATEX/
├── code/              # Source code for training, inference, and decoding
├── demo/              # Notebooks or scripts for demonstration
├── hardware/          # 3D models, wiring diagrams, sensor specs
├── images/            # Figures used in report and HTML interface
├── presentation/      # Final slides (PDF, PPTX)
├── index.html         # Self-contained webpage interface
├── LICENSE            # License file
├── README.md          # You’re reading it!
├── requirements.txt   # Python dependencies
```

---

## 🚀 Features

- ✏️ **Custom Sensor Pen**: IMU + force sensors integrated into a 3D-printed shell
- 🧠 **CLDNN Model**: Deep learning model combining CNN, LSTM, and dense layers
- 🔤 **CTC Decoding**: Converts sequential sensor data into readable character sequences
- 🌐 **Web Interface**: Interactive `index.html` for viewing results and visuals
- 🎥 **Demo Videos**: Sample outputs of real-time handwriting recognition
- 📊 **Evaluation Metrics**: Accuracy benchmarks and visualizations included

---

## ⚙️ Setup Instructions

### 1. Clone or Download the Repository

```bash
git clone https://github.com/yourusername/NEVERLATEX.git
cd NEVERLATEX
```

### 2. Create a Python Environment & Install Dependencies

```bash
pip install -r requirements.txt
```

> 💡 Recommended: Use a virtual environment (e.g., `venv` or `conda`)

---

## 🌐 Run the HTML Webpage Locally

Use Python’s built-in server:

```bash
python -m http.server 8000
```

Then open your browser and go to: [http://localhost:8000](http://localhost:8000)

---

## 🧠 Model Overview

The system uses a **CLDNN architecture** trained with **CTC Loss** for flexible character alignment. Features include:

- Convolutional layers to extract spatial features from multi-sensor input
- Bidirectional LSTMs for temporal modeling
- Dense layers for classification
- CTC Loss for alignment-free training
- Beam search decoding with KenLM language model integration

The model was pretrained on the OnHW dataset and fine-tuned on our sensor pen data.

---

## 📊 Evaluation & Performance

- Accuracy: **68.13%** with beam search decoding
- Real-time prediction: Achieved using overlapping sliding window inference
- Fine-tuned preprocessing pipeline: Including signal cleaning, normalization, and derivative features

---

## 🧪 Demo & Output Samples

- Try `demo/` for sample notebooks, including:
  - Preprocessing steps
  - Real-time sliding window decoding
  - CTC vs. cross-entropy comparison

- Check `images/` for architecture diagrams and visualizations

---

## 🛠 Hardware Setup

- Built with Arduino + Grove IMU + Ohmite force sensors
- 3D-printed case with embedded wiring and sensor support
- Breadboard setup with wired data collection

For schematics and assembly instructions, see `hardware/`.

---

## 📽 Presentation & Video

- Final presentation slides are located in the `presentation/` folder
- A short demo video is also available in the zipped package for submission

---

## 📄 License

This project is licensed under the MIT License. See `LICENSE` for more information.

---

## 👨‍💻 Authors

- Antonio Tarizzo
- Tuna Kisaaga
- Fajar Kenichi Kusumah Putra

With support from the Applied Machine Learning course team at Imperial College London.

---

## 📬 Contact

For questions or collaborations, feel free to reach out through the course communication channels or GitHub.
