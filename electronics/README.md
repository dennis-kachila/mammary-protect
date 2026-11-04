# Electronics architecture (proposed)

No verified Mammary Protect circuit schematic, PCB layout, or fabrication files were found in the local project folders inspected for this release. This page records the intended blocks; it is **not** a working circuit.

```mermaid
flowchart LR
    U[Ultrasound transducer] --> A[Transmit/receive and analog front end]
    A --> D[Digitization]
    T[Temperature sensors] --> C[Controller / data acquisition]
    D --> C
    C --> S[Storage and review software]
    P[Power and protection] --> A
    P --> C
```

The exploratory probe discussed in project notes was a single 5 MHz dual-element industrial probe. A single mechanically moved probe would not require an array multiplexer, but imaging performance and transducer suitability remain unresolved. The exact pulse/receive circuit, analog gain, sampling rate, power architecture, and sensor selection have not been finalized.

External ultrasound projects discussed in research chats were references, not original Mammary Protect circuit designs. No external schematic is reproduced here.
