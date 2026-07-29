\documentclass[11pt,a4paper]{book}

\usepackage[a4paper,margin=1in]{geometry}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{hyperref}
\usepackage{enumitem}
\usepackage{titlesec}

\hypersetup{
    colorlinks=true,
    urlcolor=blue,
    linkcolor=black
}

\setlength{\parskip}{0.6em}
\setlength{\parindent}{0pt}

\title{\textbf{Engineering Notebook}}
\author{}
\date{}

\begin{document}

\maketitle

\begin{center}
\begin{tabular}{ll}
\textbf{Project:} & Union Pacific HO Scale Railroad \\
\textbf{Project Start:} & 29 July 2026 \\
\textbf{Version:} & 0.1 \\
\end{tabular}
\end{center}

\hrule
\vspace{1em}

\section*{Engineering Log}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\section*{25 July 2026}

\subsection*{Milestone}

Started exploring a suitable DCC system for my layout, which is currently under construction.

Consulted ChatGPT extensively over multiple days regarding the architecture and component selection:

\url{https://chatgpt.com/c/6a646941-70c8-83ee-a626-fd9a4bccfce1}

Created this repository and its initial contents. This engineering notebook will continue to evolve as the railroad project progresses.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\section*{29 July 2026}

\subsection*{Milestone}

Project officially initiated with the selection of the \textbf{DCC-EX} ecosystem as the foundation for the railroad control system.

\subsection*{Procurement}

\textbf{Vendor}

\texttt{store.dcc-ex.com}

\vspace{0.5em}

\textbf{Items Ordered}

\begin{itemize}[leftmargin=2em]
    \item EX-CSB1 Express Commander Command System
    \item 15 V / 5 A regulated power supply
    \item Snap-fit enclosure
\end{itemize}

\subsection*{Engineering Decision}

After evaluating commercially available DCC systems, the \textbf{DCC-EX} platform was selected because it provides:

\begin{itemize}[leftmargin=2em]
    \item Open architecture
    \item Excellent integration with JMRI
    \item Expandable multi-booster capability
    \item Native support for modern IP networking
    \item Strong community support
    \item Ability to integrate with custom ESP32-based distributed controllers
\end{itemize}

The project intentionally avoids proprietary accessory ecosystems wherever practical in order to maximize interoperability, maintainability, and future expansion.

\subsection*{Immediate Objectives}

\begin{enumerate}[leftmargin=2em]
    \item Commission the EX-CSB1.
    \item Install JMRI on the Cubietruck.
    \item Verify OpenJDK 17 compatibility.
    \item Connect using WiThrottle.
    \item Read and program locomotive decoders.
    \item Familiarise with the DCC-EX software ecosystem.
\end{enumerate}

\vfill

\begin{center}
\textit{"A reliable railroad begins with a reliable architecture."}
\end{center}

\end{document}
