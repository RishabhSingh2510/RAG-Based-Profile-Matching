"""
create_sample_resumes.py - Generate Sample Resume Files (.pdf, .docx, .txt)

Generates 33 realistic dummy resumes in a `./resumes/` folder across PDF, DOCX, and TXT formats.
These resumes cover diverse roles, skill sets, experience levels, and domains to clearly
demonstrate RAG (Retrieval-Augmented Generation), vector semantic search, hybrid retrieval,
and candidate filtering capabilities.
"""

from pathlib import Path
import docx
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

RESUMES_DIR = Path("resumes")


def create_txt_resume(filename: str, content: str):
    filepath = RESUMES_DIR / filename
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[Created TXT] {filepath}")


def create_docx_resume(filename: str, title: str, sections: list):
    doc = docx.Document()
    doc.add_heading(title, 0)

    for heading, text in sections:
        doc.add_heading(heading, level=1)
        for line in text.split("\n"):
            if line.strip():
                doc.add_paragraph(line)

    filepath = RESUMES_DIR / filename
    doc.save(str(filepath))
    print(f"[Created DOCX] {filepath}")


def create_pdf_resume(filename: str, title: str, sections: list):
    filepath = RESUMES_DIR / filename
    doc = SimpleDocTemplate(str(filepath), pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph(title, styles['Title']))
    story.append(Spacer(1, 12))

    for heading, text in sections:
        story.append(Paragraph(heading, styles['Heading2']))
        formatted_text = text.replace('\n', '<br/>')
        story.append(Paragraph(formatted_text, styles['Normal']))
        story.append(Spacer(1, 10))

    doc.build(story)
    print(f"[Created PDF] {filepath}")


def main():
    RESUMES_DIR.mkdir(parents=True, exist_ok=True)
    print("Generating 33 diverse sample resumes in './resumes/' folder...\n")

    # =========================================================================
    # 1. John Doe (PDF) - Senior AI & LLM Systems Engineer
    # =========================================================================
    create_pdf_resume(
        "resume_john_doe.pdf",
        "John Doe - Senior AI & LLM Systems Engineer",
        [
            ("Contact Information", "Email: john.doe@email.com | Phone: (555) 019-2831 | Location: San Francisco, CA"),
            ("Professional Summary", "Senior AI Engineer with 7+ years of experience building scalable backend microservices, autonomous LLM agents, tool-calling pipelines, and production RAG (Retrieval-Augmented Generation) systems in Python."),
            ("Technical Skills", "Languages: Python, C++, SQL, Bash\nFrameworks: FastAPI, PyTorch, LangChain, LlamaIndex, TensorFlow, Django\nVector DBs: ChromaDB, Pinecone, Qdrant\nTools & Cloud: Docker, Kubernetes, Git, PostgreSQL, AWS"),
            ("Work Experience", "Senior AI Engineer - TechCorp Solutions (2022 - Present)\n- Designed and deployed enterprise LLM agents with tool calling and vector retrieval (ChromaDB), reducing query resolution time by 40%.\n- Built async Python microservices handling 15M+ daily requests with 99.9% uptime.\n\nBackend Developer - DataFlow Inc. (2018 - 2022)\n- Developed real-time telemetry processing pipelines handling 10M+ daily events in Python and Kafka."),
            ("Education", "B.S. in Computer Science - Stanford University")
        ]
    )

    # =========================================================================
    # 2. Jane Smith (DOCX) - Lead Full Stack Web Developer
    # =========================================================================
    create_docx_resume(
        "resume_jane_smith.docx",
        "Jane Smith - Lead Full Stack Web Developer",
        [
            ("Contact", "Email: jane.smith@webdev.io | Phone: (555) 014-8899 | Location: Seattle, WA"),
            ("Summary", "Creative Lead Full Stack Developer with 6+ years experience architecting modern web applications using React, TypeScript, Next.js, Node.js, and GraphQL."),
            ("Skills", "Frontend: React, Next.js, Vue.js, TypeScript, JavaScript, HTML5, CSS3, Tailwind CSS\nBackend: Node.js, Express, GraphQL, REST APIs, PostgreSQL, MongoDB, Redis"),
            ("Experience", "Lead Developer - CloudVibe Systems (2021 - Present)\n- Architected React & Next.js dashboards serving 500k+ active monthly users.\n- Reduced frontend bundle load time by 45% using code splitting and server components.\n\nFull Stack Engineer - WebFront Media (2018 - 2021)\n- Developed Node.js REST and GraphQL microservices for e-commerce clients."),
            ("Education", "B.S. in Software Engineering - University of Washington")
        ]
    )

    # =========================================================================
    # 3. Alice Johnson (TXT) - Senior Data Scientist
    # =========================================================================
    alice_content = """Alice Johnson - Senior Data Scientist
==================================================
Contact: alice.johnson@datascience.net | (555) 012-3456 | Boston, MA

PROFESSIONAL SUMMARY:
Data Scientist with 5 years experience applying Machine Learning, Natural Language Processing (NLP), and Statistical Analytics using Python, Pandas, PyTorch, and SQL.

TECHNICAL SKILLS:
- Core Languages: Python, R, SQL, Julia
- Machine Learning & NLP: Scikit-Learn, XGBoost, PyTorch, HuggingFace Transformers, SpaCy
- Big Data & Warehousing: Pandas, NumPy, Apache Spark, Snowflake, Airflow

WORK EXPERIENCE:
Senior Data Scientist | Analytics Global (2021 - Present)
- Developed customer churn prediction models in Python resulting in a 15% improvement in retention.
- Fine-tuned transformer models (BERT) for sentiment analysis across customer review feeds.

Data Analyst | Insight Tech (2019 - 2021)
- Built interactive Tableau dashboards and optimized SQL analytical queries for business intelligence.

EDUCATION:
M.S. in Statistics - UC Berkeley
B.S. in Mathematics - MIT
"""
    create_txt_resume("resume_alice_johnson.txt", alice_content)

    # =========================================================================
    # 4. Bob Williams (PDF) - DevOps & Cloud Architect
    # =========================================================================
    create_pdf_resume(
        "resume_bob_williams.pdf",
        "Bob Williams - DevOps & Cloud Architect",
        [
            ("Contact", "Email: bob.williams@cloudops.com | Phone: (555) 018-9922 | Location: Austin, TX"),
            ("Summary", "Principal DevOps Engineer with 8+ years experience managing cloud infrastructure on AWS and GCP using Terraform, Ansible, and Kubernetes."),
            ("Skills", "Cloud Platforms: AWS (EC2, EKS, S3, RDS), GCP, Azure\nInfrastructure as Code: Terraform, Ansible, CloudFormation\nContainers & Orchestration: Docker, Kubernetes, Helm\nCI/CD & Scripting: GitHub Actions, Jenkins, Python, Bash, Go"),
            ("Experience", "Lead Cloud Architect - InfraScale Tech (2020 - Present)\n- Automated Kubernetes cluster provisioning on AWS with Terraform, reducing setup time from 3 days to 15 minutes.\n- Implemented GitOps workflow using ArgoCD and GitHub Actions.\n\nDevOps Engineer - SysNet Solutions (2016 - 2020)\n- Managed CI/CD build pipelines and zero-downtime blue/green deployments."),
            ("Certifications", "AWS Certified Solutions Architect - Professional | Certified Kubernetes Administrator (CKA)")
        ]
    )

    # =========================================================================
    # 5. Charlie Brown (DOCX) - Lead Cybersecurity Specialist
    # =========================================================================
    create_docx_resume(
        "resume_charlie_brown.docx",
        "Charlie Brown - Lead Cybersecurity Specialist",
        [
            ("Contact Info", "Email: charlie.brown@secops.io | Phone: (555) 017-4433 | Location: Washington, DC"),
            ("Summary", "Security Engineer with 7 years specializing in penetration testing, threat modeling, security compliance (SOC 2, ISO 27001), and vulnerability assessments."),
            ("Key Competencies", "Security Tools: Metasploit, Wireshark, Burp Suite, Nmap, Nessus, Splunk\nDomains: Penetration Testing, Application Security, IAM, Network Security\nScripting: Python, PowerShell, Bash"),
            ("Experience", "Senior Security Engineer - CyberShield Defense (2021 - Present)\n- Conducted penetration tests across web apps and API endpoints, finding 30+ critical vulnerabilities.\n- Built automated static application security testing (SAST) scripts integrated into CI/CD.\n\nSecurity Analyst - DefenseTech Inc. (2017 - 2021)\n- Managed SIEM log monitoring with Splunk and responded to security incidents."),
            ("Certifications", "CISSP (Certified Information Systems Security Professional) | CEH (Certified Ethical Hacker)")
        ]
    )

    # =========================================================================
    # 6. Diana Prince (TXT) - Principal Backend Engineer (Java & Go)
    # =========================================================================
    diana_content = """Diana Prince - Principal Backend Engineer
==================================================
Contact: diana.prince@backendlabs.org | (555) 013-7711 | New York, NY

SUMMARY:
Principal Backend Engineer with 9 years experience architecting high-throughput distributed systems in Java, Go, C#, and PostgreSQL.

SKILLS:
- Primary Languages: Java, Go, SQL, C++, C#
- Frameworks: Spring Boot, Quarkus, gRPC, Hibernate, Microservices
- Data Stores: PostgreSQL, Redis, Apache Cassandra, Kafka

EXPERIENCE:
Principal Engineer | Enterprise Cloud Systems (2020 - Present)
- Migrated legacy monolithic architecture to Java Spring Boot microservices handling 50k req/sec with <20ms latency.
- Designed event-driven data ingestion pipeline using Apache Kafka and Go.

Senior Java Developer | Banking Solutions Corp (2015 - 2020)
- Engineered financial transaction processing systems compliant with PCI-DSS standards.

EDUCATION:
B.S. in Computer Science - Carnegie Mellon University
"""
    create_txt_resume("resume_diana_prince.txt", diana_content)

    # =========================================================================
    # 7. Evan Wright (PDF) - Senior Data Engineer
    # =========================================================================
    create_pdf_resume(
        "resume_evan_wright.pdf",
        "Evan Wright - Senior Data Engineer",
        [
            ("Contact", "Email: evan.wright@bigdata.io | Phone: (555) 021-9988 | Location: Chicago, IL"),
            ("Summary", "Data Engineer with 6 years experience constructing enterprise ETL/ELT data pipelines using PySpark, Apache Airflow, Databricks, Snowflake, and dbt."),
            ("Technical Skills", "Big Data: Apache Spark, PySpark, Databricks, Apache Airflow, Kafka, Hadoop\nData Warehouses: Snowflake, BigQuery, AWS Redshift\nLanguages & Tools: Python, SQL, Scala, dbt, Docker, Git"),
            ("Work Experience", "Senior Data Engineer - DataMesh Corp (2021 - Present)\n- Built automated Snowflake and dbt data models ingesting 5TB+ daily raw data.\n- Orchestrated complex PySpark data transformation jobs using Apache Airflow.\n\nData Pipeline Developer - RetailAnalytics (2018 - 2021)\n- Migrated legacy SQL ETL jobs to Spark on Databricks, cutting pipeline execution time by 60%."),
            ("Education", "B.S. in Information Systems - University of Illinois Urbana-Champaign")
        ]
    )

    # =========================================================================
    # 8. Fiona Chen (DOCX) - Computer Vision & Robotics Specialist
    # =========================================================================
    create_docx_resume(
        "resume_fiona_chen.docx",
        "Fiona Chen - Computer Vision & Robotics Specialist",
        [
            ("Contact", "Email: fiona.chen@roboticslab.ai | Phone: (555) 022-3344 | Location: Pittsburgh, PA"),
            ("Summary", "Robotics and Computer Vision Engineer with 5 years experience building real-time perception models, YOLO object detectors, ROS2 nodes, and CUDA-accelerated C++ pipelines."),
            ("Technical Expertise", "Computer Vision: OpenCV, YOLO, PyTorch, TensorRT, Segment Anything (SAM)\nRobotics & Hardware: ROS2, Gazebo, LiDAR, Sensor Fusion, CUDA, C++, Python\nPlatforms: NVIDIA Jetson, Linux, ROS"),
            ("Experience", "Robotics AI Engineer - AutoNav Robotics (2021 - Present)\n- Developed ROS2 C++ package for real-time 3D object detection running at 60 FPS on NVIDIA Jetson.\n- Trained YOLO models for obstacle detection with 98.2% precision.\n\nComputer Vision Researcher - VisionLab (2019 - 2021)\n- Built camera calibration and optical flow algorithms in OpenCV and Python."),
            ("Education", "M.S. in Robotics - Carnegie Mellon University")
        ]
    )

    # =========================================================================
    # 9. George Kumar (TXT) - Cross-Platform Mobile Application Developer
    # =========================================================================
    george_content = """George Kumar - Senior Mobile Application Developer
==================================================
Contact: george.kumar@mobiledev.org | (555) 023-4455 | San Jose, CA

SUMMARY:
Mobile Developer with 6 years experience crafting iOS and Android applications using Flutter, React Native, Swift, and Kotlin.

TECHNICAL SKILLS:
- Mobile Frameworks: Flutter, React Native, iOS SDK, Android SDK
- Languages: Dart, Swift, Kotlin, JavaScript, TypeScript
- Tools & Services: Firebase, REST APIs, GraphQL, App Store Connect, Google Play Console

WORK EXPERIENCE:
Lead Mobile Developer | AppSphere Technologies (2021 - Present)
- Launched cross-platform Flutter app achieving 1M+ downloads across iOS and Android.
- Integrated offline state synchronization and push notification pipelines.

iOS Developer | NextGen Apps (2018 - 2021)
- Developed native iOS apps in Swift using SwiftUI and Combine framework.

EDUCATION:
B.S. in Computer Science - San Jose State University
"""
    create_txt_resume("resume_george_kumar.txt", george_content)

    # =========================================================================
    # 10. Hannah Abbott (PDF) - AI Research Scientist (LLM Pretraining & NLP)
    # =========================================================================
    create_pdf_resume(
        "resume_hannah_abbott.pdf",
        "Dr. Hannah Abbott - AI Research Scientist",
        [
            ("Contact", "Email: hannah.abbott@airesearch.org | Phone: (555) 024-5566 | Location: Cambridge, MA"),
            ("Summary", "Ph.D. AI Research Scientist specializing in Transformer architecture, LLM pretraining, RLHF (Reinforcement Learning from Human Feedback), and parameter-efficient fine-tuning (LoRA, QLoRA)."),
            ("Skills", "Deep Learning: PyTorch, HuggingFace, DeepSpeed, Megatron-LM, JAX\nConcepts: Transformer Attention, LLM Pretraining, RLHF, LoRA, Alignment, Evaluation Metrics\nLanguages: Python, C++, LaTeX"),
            ("Research & Work Experience", "Staff Research Scientist - OpenAI Labs (2022 - Present)\n- Co-authored 4 top-tier conference papers (NeurIPS, ICML) on parameter-efficient LLM fine-tuning.\n- Optimized distributed PyTorch training across 256 GPU clusters using DeepSpeed.\n\nAI Researcher - MIT CSAIL (2018 - 2022)\n- Researched novel attention mechanisms reducing memory complexity in long-context models."),
            ("Education", "Ph.D. in Computer Science (Artificial Intelligence) - MIT\nB.S. in Applied Math - Harvard University")
        ]
    )

    # =========================================================================
    # 11. Ian Murphy (DOCX) - Technical Product Manager (AI & Data)
    # =========================================================================
    create_docx_resume(
        "resume_ian_murphy.docx",
        "Ian Murphy - Technical Product Manager (AI & Data)",
        [
            ("Contact", "Email: ian.murphy@productleadership.com | Phone: (555) 025-6677 | Location: New York, NY"),
            ("Summary", "Technical Product Manager with 7 years of experience leading cross-functional AI, Machine Learning, and Data Analytics product teams from concept to enterprise launch."),
            ("Core Competencies", "Product Strategy: AI Product Lifecycle, PRD Creation, Roadmap Planning, Market Research\nMethodologies: Agile/Scrum, User Stories, A/B Testing, Feature Prioritization\nTechnical Tools: Jira, Confluence, SQL, Amplitude, Tableau, Figma"),
            ("Experience", "Senior Product Manager - AI Products | DataTech Solutions (2021 - Present)\n- Led product vision for enterprise RAG document assistant, growing ARR by $3.2M in 18 months.\n- Managed a team of 12 engineers and data scientists following Scrum methodology.\n\nProduct Manager - E-Commerce Analytics | ShopSmart (2017 - 2021)\n- Shipped recommendation algorithm features increasing checkout conversion rate by 12%."),
            ("Education", "MBA - Columbia Business School\nB.S. in Computer Science - Cornell University")
        ]
    )

    # =========================================================================
    # 12. Julia Roberts (TXT) - UI/UX Designer & Frontend Engineer
    # =========================================================================
    julia_content = """Julia Roberts - UI/UX Designer & Frontend Engineer
==================================================
Contact: julia.roberts@designcode.io | (555) 026-7788 | Los Angeles, CA

SUMMARY:
UI/UX Design Engineer with 5 years experience creating accessible, visually stunning design systems and implementing them in React, CSS3, and Tailwind CSS.

SKILLS & TOOLS:
- Design: Figma, Adobe XD, Wireframing, Prototyping, User Research, Design Systems
- Frontend Code: HTML5, CSS3, JavaScript, TypeScript, React, Tailwind CSS, Storybook
- Accessibility: WCAG 2.1 AA Compliance, Screen Reader Optimization

EXPERIENCE:
Lead UX Engineer | Creative Canvas Studio (2021 - Present)
- Built comprehensive enterprise design system in Figma and implemented it in React & Storybook.
- Conducted user testing sessions with 50+ participants to improve onboarding workflow.

UI Designer | WebCraft Agency (2019 - 2021)
- Designed modern web and mobile UI layouts for fintech and healthcare clients.

EDUCATION:
B.F.A. in Interaction Design - Rhode Island School of Design (RISD)
"""
    create_txt_resume("resume_julia_roberts.txt", julia_content)

    # =========================================================================
    # 13. Kevin Zhang (PDF) - High-Performance Systems Engineer (Rust & C++)
    # =========================================================================
    create_pdf_resume(
        "resume_kevin_zhang.pdf",
        "Kevin Zhang - High-Performance Systems Engineer",
        [
            ("Contact", "Email: kevin.zhang@systems.dev | Phone: (555) 027-8899 | Location: Chicago, IL"),
            ("Summary", "Systems Software Engineer with 6 years experience writing ultra-low latency, concurrent, memory-safe network applications in Rust, C++, and Linux kernel programming."),
            ("Technical Skills", "Languages: Rust, C++17/20, C, Go, Assembly, POSIX\nSystems Concepts: Multithreading, Lock-free Data Structures, Async I/O (tokio, io_uring), gRPC, Memory Management\nTools: GDB, Valgrind, Perf, Git, Linux"),
            ("Work Experience", "Senior Systems Engineer - HighFrequency Tech (2021 - Present)\n- Built Rust microservices processing order book events in under 5 microseconds.\n- Optimized memory allocations in C++ trade execution engine using custom lock-free queues.\n\nSystems Developer - InfraCore (2018 - 2021)\n- Developed async network proxies and load balancers using Rust Tokio."),
            ("Education", "B.S. in Computer Engineering - University of Michigan")
        ]
    )

    # =========================================================================
    # 14. Laura Martinez (DOCX) - QA Lead & Test Automation Engineer
    # =========================================================================
    create_docx_resume(
        "resume_laura_martinez.docx",
        "Laura Martinez - QA Lead & Test Automation Engineer",
        [
            ("Contact", "Email: laura.martinez@qatech.com | Phone: (555) 028-9900 | Location: Miami, FL"),
            ("Summary", "QA Automation Lead with 7 years experience designing robust automated testing frameworks for web, API, and mobile applications using Playwright, Selenium, PyTest, and Cypress."),
            ("Technical Skills", "Test Frameworks: Playwright, PyTest, Selenium WebDriver, Cypress, Postman, JUnit\nLanguages: Python, JavaScript, Java\nCI/CD Integration: GitHub Actions, Jenkins, Allure Reports, Docker"),
            ("Work Experience", "QA Lead - QualityFirst Software (2020 - Present)\n- Built end-to-end Python Playwright automation suite covering 400+ regression test scenarios.\n- Integrated automated test runs into CI/CD pipelines, catching 95% of critical bugs prior to release.\n\nSenior QA Engineer - TestMatrix (2017 - 2020)\n- Developed REST API test suites using PyTest and Postman Newman runner."),
            ("Certifications", "ISTQB Certified Tester - Advanced Level Technical Test Analyst")
        ]
    )

    # =========================================================================
    # 15. Marcus Vance (TXT) - Site Reliability Engineer (SRE)
    # =========================================================================
    marcus_content = """Marcus Vance - Principal Site Reliability Engineer (SRE)
==================================================
Contact: marcus.vance@srecloud.net | (555) 029-1122 | Denver, CO

SUMMARY:
Site Reliability Engineer with 8 years experience optimizing system availability, building telemetry monitoring dashboards (Prometheus & Grafana), and running Chaos Engineering experiments.

TECHNICAL SKILLS:
- Monitoring & Observability: Prometheus, Grafana, Datadog, OpenTelemetry, ELK Stack
- Cloud & Orchestration: Kubernetes, Docker, AWS, GCP, Terraform
- Scripting & Automation: Go, Python, Bash, Ansible
- SRE Practices: SLO/SLA Management, Incident Response, Post-mortems, Chaos Engineering

WORK EXPERIENCE:
Principal SRE | Reliability Cloud (2020 - Present)
- Maintained 99.99% system availability across multi-region Kubernetes clusters.
- Configured OpenTelemetry tracing and Prometheus alerting rules for 100+ microservices.

SRE Engineer | ScaleUp Systems (2016 - 2020)
- Automated incident management triage workflows in Go and Python.

EDUCATION:
B.S. in Computer Science - University of Colorado Boulder
"""
    create_txt_resume("resume_marcus_vance.txt", marcus_content)

    # =========================================================================
    # 16. Nina Patel (PDF) - Healthcare Data Scientist (NLP & HIPAA)
    # =========================================================================
    create_pdf_resume(
        "resume_nina_patel.pdf",
        "Nina Patel - Healthcare Data Scientist",
        [
            ("Contact", "Email: nina.patel@healthai.org | Phone: (555) 030-2233 | Location: Atlanta, GA"),
            ("Summary", "Healthcare Data Scientist with 5 years experience analyzing Electronic Health Records (EHR), medical imaging, and clinical text using NLP, PyTorch, and HIPAA-compliant data pipelines."),
            ("Technical Skills", "ML & Bio-NLP: PyTorch, BioBERT, SpaCy Clinical, Scikit-learn, DICOM, MONAI\nHealthcare Standards: HIPAA, FHIR, ICD-10, SNOMED CT\nData & Programming: Python, R, SQL, PostgreSQL, AWS HealthLake"),
            ("Work Experience", "Senior Healthcare Data Scientist - BioHealth Solutions (2021 - Present)\n- Developed NLP pipeline extracting diagnosis codes from unstructured doctor notes with 94% F1-score.\n- Designed HIPAA-compliant anonymization module for clinical datasets.\n\nBiomedical Data Analyst - Emory Health (2019 - 2021)\n- Processed MRI and CT DICOM scans for computer vision classification models."),
            ("Education", "M.S. in Biomedical Informatics - Emory University\nB.S. in Computer Science - Georgia Tech")
        ]
    )

    # =========================================================================
    # 17. Oliver Queen (DOCX) - Blockchain & Smart Contract Developer
    # =========================================================================
    create_docx_resume(
        "resume_oliver_queen.docx",
        "Oliver Queen - Blockchain & Smart Contract Developer",
        [
            ("Contact", "Email: oliver.queen@web3dev.io | Phone: (555) 031-3344 | Location: Austin, TX"),
            ("Summary", "Blockchain Engineer with 4 years experience writing secure Solidity smart contracts, building DeFi protocols, and performing smart contract security audits."),
            ("Technical Skills", "Blockchain: Ethereum, Solidity, Hardhat, Foundry, Web3.js, Ethers.js, Rust (Anchor/Solana)\nDeveloper Tools: Remix, OpenZeppelin, Slither, IPFS\nBackend: Node.js, TypeScript, Go"),
            ("Experience", "Lead Smart Contract Developer - DecentralFi Labs (2022 - Present)\n- Deployed audited Solidity liquidity pool contracts holding $20M+ Total Value Locked (TVL).\n- Optimized gas consumption across ERC-20 and ERC-721 token contracts by 25%.\n\nBlockchain Developer - CryptoTech (2020 - 2022)\n- Built dApps interacting with Ethereum and Polygon networks using Web3.js."),
            ("Education", "B.S. in Computer Science - University of Texas at Austin")
        ]
    )

    # =========================================================================
    # 18. Paula Foster (TXT) - Database Administrator & SQL Specialist
    # =========================================================================
    paula_content = """Paula Foster - Senior Database Administrator & SQL Engineer
==================================================
Contact: paula.foster@dbexperts.com | (555) 032-4455 | Dallas, TX

SUMMARY:
Senior Database Administrator with 8 years experience managing high-availability PostgreSQL, MySQL, Redis, and Cassandra database clusters, query optimization, and disaster recovery.

TECHNICAL SKILLS:
- Relational DBs: PostgreSQL, MySQL, Oracle DB, SQL Server
- NoSQL & Caching: Redis, Apache Cassandra, MongoDB
- Optimization: SQL Query Tuning, Indexing Strategies, Execution Plan Analysis, PgBouncer
- Administration: Database Replication, Backup/Recovery, Vacuuming, Patches

WORK EXPERIENCE:
Lead DBA | Enterprise Data Systems (2019 - Present)
- Managed 50+ PostgreSQL production databases supporting high-traffic payment processing.
- Optimized slow SQL queries, achieving a 70% decrease in database CPU utilization.

Database Analyst | Financial Data Corp (2016 - 2019)
- Executed automated database backup and point-in-time recovery testing scripts.

EDUCATION:
B.S. in Information Technology - University of North Texas
"""
    create_txt_resume("resume_paula_foster.txt", paula_content)

    # =========================================================================
    # 19. Quinn Taylor (PDF) - Embedded Systems & IoT Firmware Engineer
    # =========================================================================
    create_pdf_resume(
        "resume_quinn_taylor.pdf",
        "Quinn Taylor - Embedded Systems & IoT Firmware Engineer",
        [
            ("Contact", "Email: quinn.taylor@embedded.dev | Phone: (555) 033-5566 | Location: Phoenix, AZ"),
            ("Summary", "Embedded Software Engineer with 6 years experience writing real-time C/C++ firmware for ARM Cortex microcontrollers, FreeRTOS, ESP32, and IoT wireless protocols."),
            ("Technical Skills", "Languages: C, Embedded C++, Python, Assembly\nRTOS & Microcontrollers: FreeRTOS, ARM Cortex-M, ESP32, STM32, Nordic nRF52\nProtocols: BLE, Wi-Fi, MQTT, I2C, SPI, UART, CAN bus\nHardware Tools: Oscilloscopes, Logic Analyzers, JTAG, KiCad"),
            ("Work Experience", "Senior Firmware Engineer - IoT Tech Devices (2021 - Present)\n- Developed FreeRTOS C++ firmware for battery-powered BLE environmental sensors.\n- Reduced deep-sleep power consumption by 50%, extending battery life to 3 years.\n\nEmbedded Software Engineer - SensorNet (2018 - 2021)\n- Programmed STM32 microcontrollers using C and HAL drivers for automotive CAN communication."),
            ("Education", "B.S. in Electrical & Computer Engineering - Arizona State University")
        ]
    )

    # =========================================================================
    # 20. Rachel Green (DOCX) - MLOps Engineer (Model Deployment & Tracking)
    # =========================================================================
    create_docx_resume(
        "resume_rachel_green.docx",
        "Rachel Green - Senior MLOps Engineer",
        [
            ("Contact", "Email: rachel.green@mlops.io | Phone: (555) 034-6677 | Location: San Francisco, CA"),
            ("Summary", "MLOps Engineer with 5 years experience bridging machine learning and DevOps by automating model deployment pipelines using MLflow, Kubeflow, Docker, and Triton Inference Server."),
            ("Technical Skills", "MLOps Tools: MLflow, Kubeflow, DVC, Triton Inference Server, Weights & Biases\nML Frameworks: PyTorch, TensorFlow, Scikit-learn, ONNX\nCloud & Infrastructure: Docker, Kubernetes, AWS SageMaker, Terraform, Python, CI/CD"),
            ("Work Experience", "Senior MLOps Engineer - AI Pipeline Solutions (2021 - Present)\n- Automated end-to-end model retraining and deployment pipeline on Kubernetes using Kubeflow and MLflow.\n- Converted PyTorch models to ONNX and deployed on Triton Inference Server, reducing latency by 40%.\n\nMachine Learning Engineer - DataPulse (2019 - 2021)\n- Monitored model drift and prediction latency for production credit scoring models."),
            ("Education", "M.S. in Computer Science - Stanford University")
        ]
    )

    # =========================================================================
    # 21. Samuel Jackson (TXT) - Enterprise Solutions Architect
    # =========================================================================
    samuel_content = """Samuel Jackson - Enterprise Solutions Architect
==================================================
Contact: samuel.jackson@enterprise-arch.com | (555) 035-7788 | Atlanta, GA

SUMMARY:
Enterprise Solutions Architect with 12+ years experience advising Fortune 500 companies on cloud modernization, microservice transition, enterprise governance, and TOGAF architecture patterns.

KEY SKILLS:
- Architecture Frameworks: TOGAF, Domain-Driven Design (DDD), Microservices Architecture, Event-Driven Systems
- Cloud & Platforms: AWS, Azure, Google Cloud Platform, VMware, Salesforce Integrations
- Leadership: Enterprise Strategy, Executive Stakeholder Alignment, Tech Stack Rationalization

WORK EXPERIENCE:
Principal Solutions Architect | Global Enterprise Consulting (2018 - Present)
- Led legacy-to-cloud digital transformation for a $2B financial institution, reducing IT infrastructure cost by 30%.
- Authored cloud architecture blueprints for multi-tenant microservices on AWS.

Chief Architect | TechCorp Global (2012 - 2018)
- Governed technical strategy and architecture standards across 500+ software developers.

EDUCATION:
M.S. in Software Engineering - Georgia Tech
Certifications: TOGAF 9 Certified Architect | AWS Certified Solutions Architect Professional
"""
    create_txt_resume("resume_samuel_jackson.txt", samuel_content)

    # =========================================================================
    # 22. Tina Fey (PDF) - Junior Python Developer (Entry Level)
    # =========================================================================
    create_pdf_resume(
        "resume_tina_fey.pdf",
        "Tina Fey - Junior Python Developer",
        [
            ("Contact", "Email: tina.fey@devjunior.org | Phone: (555) 036-8899 | Location: Brooklyn, NY"),
            ("Summary", "Enthusiastic Junior Python Developer with 1+ year of hands-on experience writing RESTful web applications in Django, Flask, PostgreSQL, and Git."),
            ("Technical Skills", "Languages: Python, HTML, CSS, JavaScript, SQL\nFrameworks: Django, Flask, Bootstrap\nTools: Git, GitHub, PostgreSQL, SQLite, Postman, Linux"),
            ("Work Experience", "Junior Software Developer - WebStart Studio (2023 - Present)\n- Developed Django REST framework API endpoints for e-commerce client websites.\n- Wrote unit tests in PyTest achieving 80% code coverage.\n\nSoftware Engineering Intern - CodeLaunch (2022 - 2023)\n- Assisted in debugging Python scripts and maintaining documentation."),
            ("Education", "B.S. in Computer Science - City College of New York (CCNY)")
        ]
    )

    # =========================================================================
    # 23. Umar Farooq (DOCX) - Fintech Backend Developer (Go & High-Frequency)
    # =========================================================================
    create_docx_resume(
        "resume_umar_farooq.docx",
        "Umar Farooq - Fintech Backend Developer",
        [
            ("Contact", "Email: umar.farooq@fintechdev.com | Phone: (555) 037-9900 | Location: New York, NY"),
            ("Summary", "Fintech Software Engineer with 6 years experience building high-frequency trading backend systems, payment gateways, and PCI-DSS compliant services in Go and Kafka."),
            ("Skills", "Languages: Go (Golang), C++, Python, SQL\nFintech & Systems: Payment Processing, PCI-DSS, Kafka, Redis, gRPC, PostgreSQL, Microservices\nInfrastructure: Docker, Kubernetes, AWS"),
            ("Work Experience", "Senior Go Engineer - TradeFast Capital (2021 - Present)\n- Built real-time order matching engine in Go executing 100k transactions per second.\n- Implemented PCI-DSS compliant credit card tokenization service.\n\nBackend Engineer - PayDirect (2018 - 2021)\n- Developed microservices in Go for instant bank transfer processing."),
            ("Education", "B.S. in Computer Science - Columbia University")
        ]
    )

    # =========================================================================
    # 24. Victoria Secret (TXT) - Vector Search & Information Retrieval Specialist
    # =========================================================================
    victoria_content = """Victoria Secret - Vector Search & Information Retrieval Specialist
==================================================
Contact: victoria.secret@vectorsearch.ai | (555) 038-1133 | San Francisco, CA

SUMMARY:
Information Retrieval Scientist with 5 years experience specializing in vector embeddings, dense retrieval (Pinecone, ChromaDB, Milvus, Qdrant), hybrid BM25 + dense search, and RAG evaluation metrics.

TECHNICAL SKILLS:
- Vector DBs & Indexing: Pinecone, ChromaDB, Qdrant, Milvus, FAISS, Weaviate, HNSW indexing
- Search & Retrieval: BM25, Reciprocal Rank Fusion (RRF), Cross-Encoders, RAG Triad Evaluation (Ragas, TruLens)
- Languages & Frameworks: Python, C++, PyTorch, Sentence-Transformers, LangChain, LlamaIndex

WORK EXPERIENCE:
Senior Search Engineer | SearchAI Systems (2021 - Present)
- Engineered hybrid vector search engine combining BM25 keyword matching with Pinecone dense embeddings, boosting retrieval recall@10 by 28%.
- Optimized FAISS vector indexing memory footprint by 4x using Product Quantization (PQ).

IR Researcher | DataRetrieval Labs (2019 - 2021)
- Researched dense passage retrieval (DPR) models for open-domain question answering.

EDUCATION:
M.S. in Computer Science - UC San Diego
"""
    create_txt_resume("resume_victoria_secret.txt", victoria_content)

    # =========================================================================
    # 25. William Drake (PDF) - Cloud Security & Zero Trust Specialist
    # =========================================================================
    create_pdf_resume(
        "resume_william_drake.pdf",
        "William Drake - Cloud Security & Zero Trust Specialist",
        [
            ("Contact", "Email: william.drake@cloudsec.io | Phone: (555) 039-2244 | Location: Seattle, WA"),
            ("Summary", "Cloud Security Engineer with 6 years experience implementing Zero Trust architecture, AWS Security Hub, IAM least-privilege policies, and automated Terraform security scanning."),
            ("Technical Skills", "Cloud Security: AWS IAM, AWS GuardDuty, Security Hub, Azure AD, Zero Trust, KMS\nCompliance & Governance: SOC 2, HIPAA, NIST 800-53, ISO 27001\nSecurity Tools: Checkov, tfsec, Trivy, Vault, Python, Terraform"),
            ("Work Experience", "Senior Cloud Security Engineer - SecureCloud Systems (2021 - Present)\n- Implemented Zero Trust access controls across multi-region AWS environments for 2,000+ employees.\n- Automated Terraform infrastructure security checks using Checkov in GitHub Actions pipelines.\n\nSecurity Engineer - NetDefend (2018 - 2021)\n- Audited AWS IAM roles and enforced strict least-privilege policy controls."),
            ("Certifications", "AWS Certified Security - Specialty | Certified Cloud Security Professional (CCSP)")
        ]
    )

    # =========================================================================
    # 26. Xiaowei Li (DOCX) - Autonomous Vehicle Systems Engineer
    # =========================================================================
    create_docx_resume(
        "resume_xiaowei_li.docx",
        "Xiaowei Li - Autonomous Vehicle Systems Engineer",
        [
            ("Contact", "Email: xiaowei.li@autodrive.ai | Phone: (555) 040-3355 | Location: San Jose, CA"),
            ("Summary", "Autonomous Driving Engineer with 6 years experience developing sensor fusion algorithms (LiDAR, Radar, Camera), Extended Kalman Filters, and trajectory planning in C++ and ROS2."),
            ("Technical Skills", "Algorithms: Sensor Fusion, Extended Kalman Filter (EKF), SLAM, Path Planning (A*, Lattice)\nSoftware & Frameworks: C++17, ROS2, Python, OpenCV, PCL (Point Cloud Library)\nSimulation: CARLA, Gazebo, Automotive Linux"),
            ("Work Experience", "Senior Autonomy Engineer - DriveAI Mobility (2021 - Present)\n- Developed multi-sensor LiDAR and camera tracking pipeline in C++ running real-time on autonomous shuttles.\n- Implemented trajectory planning modules passing safety tests across 100k+ simulation miles.\n\nRobotics Software Engineer - AeroRobotics (2018 - 2021)\n- Programmed SLAM localization algorithms for indoor drone navigation."),
            ("Education", "Ph.D. in Mechanical Engineering (Robotics) - Stanford University")
        ]
    )

    # =========================================================================
    # 27. Yasmine Alman (TXT) - Data Governance & Analytics Manager
    # =========================================================================
    yasmine_content = """Yasmine Alman - Data Governance & Analytics Manager
==================================================
Contact: yasmine.alman@datagov.org | (555) 041-4466 | Chicago, IL

SUMMARY:
Data Governance Manager with 7 years experience establishing enterprise data lineage, cataloging (Collibra, Alation), GDPR/CCPA data privacy compliance, and SQL analytics governance.

TECHNICAL SKILLS:
- Data Governance: Collibra, Alation, Data Lineage, Metadata Management, Master Data Management (MDM)
- Compliance & Privacy: GDPR, CCPA, HIPAA Data Auditing
- Data & Analytics: SQL, Snowflake, Tableau, PowerBI, Python

WORK EXPERIENCE:
Data Governance Manager | Enterprise Global Data (2020 - Present)
- Implemented enterprise data catalog in Collibra covering 10,000+ data assets across Snowflake.\n- Established GDPR data retention and deletion pipelines reducing compliance risk exposure.

Senior Data Analyst | Retail Insights (2017 - 2020)
- Designed executive BI dashboards in Tableau and managed master data dictionary.

EDUCATION:
M.S. in Information Management - Northwestern University
"""
    create_txt_resume("resume_yasmine_alman.txt", yasmine_content)

    # =========================================================================
    # 28. Zachary Levi (PDF) - Senior Microservices Architect (Java & Quarkus)
    # =========================================================================
    create_pdf_resume(
        "resume_zachary_levi.pdf",
        "Zachary Levi - Senior Microservices Architect",
        [
            ("Contact", "Email: zachary.levi@microarch.com | Phone: (555) 042-5577 | Location: Charlotte, NC"),
            ("Summary", "Software Architect with 10+ years experience building cloud-native event-driven microservice architectures using Java 17, Quarkus, Spring Boot, Kafka, and Docker."),
            ("Technical Skills", "Java Ecosystem: Java 17, Quarkus, Spring Boot, Hibernate, Reactive Java (Mutiny)\nEvent Streaming: Apache Kafka, RabbitMQ, Event Sourcing, CQRS\nDatabases & Cloud: PostgreSQL, Redis, Kubernetes, AWS, Docker"),
            ("Work Experience", "Lead Software Architect - CloudBank Tech (2019 - Present)\n- Architected Quarkus-based microservice architecture reducing container startup time to <500ms and memory usage by 60%.\n- Implemented CQRS and event sourcing patterns with Apache Kafka for core banking ledger.\n\nSenior Java Developer - CommerceTech (2014 - 2019)\n- Developed Spring Boot microservices handling order management."),
            ("Education", "B.S. in Computer Science - University of North Carolina at Chapel Hill")
        ]
    )

    # =========================================================================
    # 29. Amelia Earhart (DOCX) - Bioinformatics Software Specialist
    # =========================================================================
    create_docx_resume(
        "resume_amelia_earhart.docx",
        "Amelia Earhart - Bioinformatics Software Specialist",
        [
            ("Contact", "Email: amelia.earhart@genomics.org | Phone: (555) 043-6688 | Location: Boston, MA"),
            ("Summary", "Bioinformatics Software Engineer with 5 years experience designing genomic sequencing analysis pipelines (Nextflow, Snakemake), Python, R/Bioconductor, and FASTQ/BAM parsing."),
            ("Skills & Tools", "Bioinformatics Tools: Nextflow, Snakemake, Samtools, BCFTools, GATK, BLAST\nLanguages: Python, R, Bash, SQL\nData Analysis: Bioconductor, Pandas, NumPy, Variant Effect Predictor (VEP)"),
            ("Work Experience", "Bioinformatics Developer - GenomeLabs Research (2021 - Present)\n- Built automated Nextflow pipeline processing 1,000+ Whole Genome Sequencing (WGS) samples weekly on AWS batch.\n- Wrote custom Python scripts to parse VCF variant files and annotate clinical significance.\n\nComputational Biologist - BioGen Tech (2019 - 2021)\n- Performed differential gene expression analysis using R Bioconductor DESeq2 package."),
            ("Education", "M.S. in Bioinformatics - Johns Hopkins University")
        ]
    )

    # =========================================================================
    # 30. Benjamin Franklin (TXT) - Quantum Computing Researcher & Developer
    # =========================================================================
    benjamin_content = """Benjamin Franklin - Quantum Computing Researcher
==================================================
Contact: benjamin.franklin@quantumtech.io | (555) 044-7799 | Princeton, NJ

SUMMARY:
Quantum Computing Software Researcher with 4 years experience implementing quantum algorithms, variational quantum eigensolvers (VQE), and quantum circuits using Qiskit, Cirq, and Python.

TECHNICAL SKILLS:
- Quantum Frameworks: Qiskit, Google Cirq, Pennylane, PyQuil
- Mathematical & AI Foundations: Quantum Linear Algebra, VQE, QAOA, PyTorch, NumPy, SciPy
- Languages: Python, C++, LaTeX

WORK EXPERIENCE:
Quantum Software Researcher | Quantum Dynamics Inc (2022 - Present)
- Developed noise-mitigated quantum circuits in Qiskit evaluated on IBM Quantum hardware.
- Implemented hybrid quantum-classical neural network models using Pennylane and PyTorch.

Physics Research Assistant | Princeton Physics Lab (2020 - 2022)
- Simulated quantum error correction codes in Python.

EDUCATION:
Ph.D. Candidate in Physics (Quantum Information) - Princeton University
B.S. in Physics - Yale University
"""
    create_txt_resume("resume_benjamin_franklin.txt", benjamin_content)

    # =========================================================================
    # 31. Chloe Bennet (PDF) - Full Stack AI Developer (Next.js & LangChain)
    # =========================================================================
    create_pdf_resume(
        "resume_chloe_bennet.pdf",
        "Chloe Bennet - Full Stack AI Developer",
        [
            ("Contact", "Email: chloe.bennet@aidev.io | Phone: (555) 045-8800 | Location: San Francisco, CA"),
            ("Summary", "Full Stack AI Developer with 4 years experience building web interfaces and LLM-powered applications using Next.js 14, React, TypeScript, LangChain, and OpenAI/Gemini APIs."),
            ("Technical Skills", "Frontend: Next.js, React, TypeScript, Tailwind CSS, Shadcn UI\nAI Integrations: LangChain, LlamaIndex, OpenAI API, Gemini API, Vector DBs (ChromaDB)\nBackend & Deployment: Node.js, Vercel, Supabase, PostgreSQL, Fast API"),
            ("Work Experience", "Full Stack AI Developer - SmartApps Studio (2022 - Present)\n- Built Next.js web application incorporating real-time streaming RAG chatbot using LangChain and Vercel AI SDK.\n- Designed sleek modern user interfaces with Tailwind CSS and Framer Motion.\n\nFrontend Developer - WebDev Agency (2020 - 2022)\n- Developed responsive React web apps connected to REST backends."),
            ("Education", "B.S. in Computer Science - UC Berkeley")
        ]
    )

    # =========================================================================
    # 32. Daniel Craig (DOCX) - Deep Learning Computer Vision Engineer
    # =========================================================================
    create_docx_resume(
        "resume_daniel_craig.docx",
        "Daniel Craig - Deep Learning Computer Vision Engineer",
        [
            ("Contact", "Email: daniel.craig@visionai.dev | Phone: (555) 046-9911 | Location: Austin, TX"),
            ("Summary", "Deep Learning Engineer with 5 years experience specializing in object detection, instance segmentation, TensorRT model optimization, and Edge AI deployment on NVIDIA Jetson."),
            ("Technical Skills", "Deep Learning: PyTorch, TensorFlow, TensorRT, ONNX, OpenCV, YOLOv8, Detectron2\nEdge Computing: NVIDIA Jetson, DeepStream SDK, CUDA, C++, Python\nTooling: Git, Docker, Linux, Weights & Biases"),
            ("Work Experience", "Senior Vision AI Engineer - EdgeVision Labs (2021 - Present)\n- Optimized PyTorch object detection models with TensorRT, achieving 4x acceleration for real-time edge processing.\n- Deployed multi-camera video analytics system using NVIDIA DeepStream SDK.\n\nML Engineer - SmartSecurity AI (2019 - 2021)\n- Trained custom Convolutional Neural Networks (CNNs) for facial recognition."),
            ("Education", "M.S. in Electrical Engineering - UT Austin")
        ]
    )

    # =========================================================================
    # 33. Elena Rostova (TXT) - Natural Language Processing (NLP) Specialist
    # =========================================================================
    elena_content = """Elena Rostova - Natural Language Processing (NLP) Specialist
==================================================
Contact: elena.rostova@nlptech.org | (555) 047-1122 | Seattle, WA

SUMMARY:
NLP Specialist with 5 years experience developing Named Entity Recognition (NER), text classification, semantic search, and topic modeling using SpaCy, HuggingFace Transformers, and Python.

TECHNICAL SKILLS:
- NLP Frameworks: SpaCy, HuggingFace Transformers, NLTK, Gensim, Stanza
- ML & Models: BERT, RoBERTa, T5, Scikit-learn, PyTorch, FastText
- Search & Data: ElasticSearch, BM25, Python, SQL, Pandas

WORK EXPERIENCE:
Senior NLP Engineer | TextAnalytics Corp (2021 - Present)
- Fine-tuned RoBERTa models for multi-label text classification across 5M+ news articles with 92% accuracy.
- Built custom SpaCy NER pipelines extracting entity relations from financial documents.

NLP Analyst | DataStream Inc (2019 - 2021)
- Developed sentiment analysis algorithms for social media data feeds.

EDUCATION:
M.S. in Computational Linguistics - University of Washington
B.S. in Computer Science - Western Washington University
"""
    create_txt_resume("resume_elena_rostova.txt", elena_content)

    # =========================================================================
    # 34. Nathaniel Vance (PDF) - Junior Python Backend Developer
    # =========================================================================
    create_pdf_resume(
        "resume_nathaniel_vance.pdf",
        "Nathaniel Vance - Junior Python Backend Developer",
        [
            ("Contact", "Email: nathaniel.vance@backenddev.com | Phone: (555) 048-2233 | Location: Denver, CO"),
            ("Summary", "Enthusiastic Junior Python Backend Developer with 1.5 years of experience building RESTful APIs using Python, FastAPI, Django, SQLite, PostgreSQL, and Docker."),
            ("Technical Skills", "Languages & Frameworks: Python, FastAPI, Django, Flask, SQL\nDatabases & Tools: PostgreSQL, SQLite, Git, Docker, Postman, Linux"),
            ("Work Experience", "Junior Backend Developer - CodeCraft Studio (2023 - Present)\n- Developed REST API endpoints using FastAPI for user authentication and content management.\n- Integrated SQLite and PostgreSQL databases, writing optimized SQL queries.\n\nSoftware Engineering Intern - WebApp Solutions (2022 - 2023)\n- Assisted in writing unit tests with PyTest and fixing bug tickets in Django backend."),
            ("Education", "B.S. in Computer Science - University of Colorado Denver")
        ]
    )

    # =========================================================================
    # 35. Olivia Wilde (DOCX) - Senior NLP Research Scientist
    # =========================================================================
    create_docx_resume(
        "resume_olivia_wilde.docx",
        "Olivia Wilde - Senior NLP Research Scientist",
        [
            ("Contact", "Email: olivia.wilde@nlpresearch.ai | Phone: (555) 049-3344 | Location: Boston, MA"),
            ("Summary", "Senior NLP Scientist with 6 years experience conducting applied AI research and fine-tuning Large Language Models (LLMs) using PyTorch, HuggingFace Transformers, SpaCy, and BERT."),
            ("Technical Skills", "NLP & AI: PyTorch, Hugging Face, Transformers, BERT, SpaCy, NLTK, Prompt Engineering\nLanguages & Infrastructure: Python, C++, SQL, CUDA, Weights & Biases, Docker"),
            ("Work Experience", "Lead NLP Scientist - DeepText AI (2021 - Present)\n- Fine-tuned domain-specific LLaMA and BERT transformer models for biomedical entity recognition.\n- Published 3 peer-reviewed papers on parameter-efficient fine-tuning (LoRA, QLoRA).\n\nNLP Researcher - Cognition Labs (2018 - 2021)\n- Developed multilingual sentiment analysis models achieving state-of-the-art accuracy on benchmark datasets."),
            ("Education", "Ph.D. in Computer Science (NLP focus) - Harvard University")
        ]
    )

    # =========================================================================
    # 36. Patrick Stewart (TXT) - Database Administrator & Storage Engineer
    # =========================================================================
    patrick_content = """Patrick Stewart - Senior Database Administrator & Storage Engineer
==================================================
Contact: patrick.stewart@dbadmin.io | (555) 050-4455 | Dallas, TX

SUMMARY:
Senior Database Administrator with 8 years experience managing high-availability database clusters in PostgreSQL, MongoDB, Redis, and MySQL with expert query performance tuning and replication.

TECHNICAL SKILLS:
- Databases: PostgreSQL, MongoDB, Redis, MySQL, Apache Cassandra
- DB Administration: Backup/Recovery, Replication, Failover, Sharding, Query Performance Tuning, Index Optimization
- Scripting & Infrastructure: Python, Bash, Docker, Ansible, Linux Kernel Tuning

WORK EXPERIENCE:
Lead DBA | DataFortress Systems (2020 - Present)
- Managed 50+ production PostgreSQL and MongoDB clusters handling 100M+ queries daily with 99.99% availability.
- Reduced slow query latency by 65% through index optimization and vacuum configuration in PostgreSQL.

Database Administrator | FinanceCore Corp (2016 - 2020)
- Configured automated multi-region streaming replication and backup strategies.

EDUCATION:
B.S. in Information Systems - UT Dallas
"""
    create_txt_resume("resume_patrick_stewart.txt", patrick_content)

    # =========================================================================
    # 37. Quentin Tarantino (PDF) - Lead Mobile App Engineer
    # =========================================================================
    create_pdf_resume(
        "resume_quentin_tarantino.pdf",
        "Quentin Tarantino - Lead Mobile App Engineer",
        [
            ("Contact", "Email: quentin.tarantino@mobileapps.dev | Phone: (555) 051-5566 | Location: Los Angeles, CA"),
            ("Summary", "Lead Mobile Developer with 6 years experience building high-performance cross-platform and native mobile apps using Flutter, React Native, Swift (iOS), and Kotlin (Android)."),
            ("Technical Skills", "Mobile Frameworks: Flutter, React Native, Swift, Kotlin, iOS SDK, Android SDK\nBackend Services: Firebase, REST APIs, GraphQL, Supabase, SQLite\nTools & CI/CD: Fastlane, Bitrise, Git, Xcode, Android Studio"),
            ("Work Experience", "Lead Mobile Architect - AppVibe Mobile (2021 - Present)\n- Built e-commerce mobile application using Flutter with 1M+ downloads across iOS and Android.\n- Reduced app crash rate to <0.01% using Sentry crash reporting and automated CI/CD.\n\niOS Developer - MobileWorks Inc (2018 - 2021)\n- Developed native iOS apps in Swift with custom animations and CoreData persistent storage."),
            ("Education", "B.S. in Computer Science - UCLA")
        ]
    )

    # =========================================================================
    # 38. Rosamund Pike (DOCX) - Embedded Systems & Firmware Specialist
    # =========================================================================
    create_docx_resume(
        "resume_rosamund_pike.docx",
        "Rosamund Pike - Embedded Systems & Firmware Specialist",
        [
            ("Contact", "Email: rosamund.pike@embeddedtech.io | Phone: (555) 052-6677 | Location: San Jose, CA"),
            ("Summary", "Embedded Systems Engineer with 4 years experience developing low-level C and C++ firmware for microcontrollers, FreeRTOS, and Embedded Linux systems."),
            ("Technical Skills", "Languages: C, C++, Assembly, Python, Bash\nEmbedded Systems: FreeRTOS, Embedded Linux, STM32, ARM Cortex-M, ESP32, I2C, SPI, UART, CAN bus\nTools: Oscilloscopes, Logic Analyzers, GCC, GDB, Keil, Git"),
            ("Work Experience", "Senior Firmware Engineer - IoT Core Systems (2022 - Present)\n- Developed real-time telemetry firmware in C/C++ on STM32 microcontrollers using FreeRTOS.\n- Implemented secure OTA (Over-The-Air) firmware update protocol over CAN bus.\n\nEmbedded Software Engineer - Robotics Lab (2020 - 2022)\n- Wrote peripheral device drivers in C for motor controllers and IMU sensors."),
            ("Education", "B.S. in Computer Engineering - San Jose State University")
        ]
    )

    # =========================================================================
    # 39. Stephen Hawking (TXT) - High Performance Computing & HPC Engineer
    # =========================================================================
    stephen_content = """Stephen Hawking - HPC & Algorithmic Performance Engineer
==================================================
Contact: stephen.hawking@hpc-labs.org | (555) 053-7788 | Princeton, NJ

SUMMARY:
HPC Specialist with 7 years experience designing parallel computing algorithms, GPU acceleration (CUDA), MPI, and OpenMP in C++ and Python for massive scientific simulations.

TECHNICAL SKILLS:
- HPC & Parallelism: CUDA, OpenMP, MPI, C++, C, Python, Vectorization (AVX-512)
- Frameworks & Profiling: PyTorch, Nsight Systems, Valgrind, GDB, CMake, Git

WORK EXPERIENCE:
Lead HPC Architect | Supercomputing Center (2020 - Present)
- Optimized parallel matrix multiplication algorithms using CUDA on NVIDIA H100 GPUs, achieving 8x speedup.
- Scaled fluid dynamics simulations across 1,000+ compute nodes using MPI.

Performance Engineer | QuantumSim Inc (2017 - 2020)
- Profiling C++ core libraries to eliminate cache misses and memory allocation bottlenecks.

EDUCATION:
Ph.D. in Applied Physics - Princeton University
"""
    create_txt_resume("resume_stephen_hawking.txt", stephen_content)

    # =========================================================================
    # 40. Tessa Thompson (PDF) - Technical Product Manager
    # =========================================================================
    create_pdf_resume(
        "resume_tessa_thompson.pdf",
        "Tessa Thompson - Senior Technical Product Manager",
        [
            ("Contact", "Email: tessa.thompson@producttech.com | Phone: (555) 054-8899 | Location: San Francisco, CA"),
            ("Summary", "Technical Product Manager with 5 years experience driving enterprise SaaS product roadmaps, cross-functional engineering execution, Agile sprint management, and API feature delivery."),
            ("Technical Skills", "Product Management: Agile, Scrum, JIRA, Confluence, Product Roadmapping, User Stories\nTechnical Knowledge: SQL, Python, REST APIs, Microservices Architecture, A/B Testing, Analytics"),
            ("Work Experience", "Senior Product Manager - SaaSify Platforms (2021 - Present)\n- Managed developer API platform product roadmap, growing developer adoption by 120% YoY.\n- Led cross-functional team of 12 software engineers in bi-weekly Agile sprints.\n\nTechnical Program Manager - CloudSoft Inc (2019 - 2021)\n- Defined technical specifications and system architecture requirements for cloud storage microservices."),
            ("Education", "B.S. in Industrial Engineering & Computer Science - UC Berkeley")
        ]
    )

    # =========================================================================
    # 41. Ulysses Grant (DOCX) - Site Reliability Engineer (SRE)
    # =========================================================================
    create_docx_resume(
        "resume_ulysses_grant.docx",
        "Ulysses Grant - Lead Site Reliability Engineer (SRE)",
        [
            ("Contact", "Email: ulysses.grant@srelabs.net | Phone: (555) 055-9900 | Location: Seattle, WA"),
            ("Summary", "Site Reliability Engineer with 6 years experience driving system observability, SLO/SLA management, automated incident response, Prometheus monitoring, and Terraform infrastructure management."),
            ("Technical Skills", "Observability: Prometheus, Grafana, Datadog, OpenTelemetry, Jaeger, ELK Stack\nInfrastructure & Automation: Kubernetes, Terraform, Docker, Python, Go, Bash, Ansible"),
            ("Work Experience", "Lead SRE - CloudScale Systems (2021 - Present)\n- Maintained 99.99% availability across global Kubernetes infrastructure serving 20M+ requests/day.\n- Automated chaos engineering tests and reduced Mean Time to Resolution (MTTR) by 50%.\n\nDevOps & SRE Engineer - DataPipeline Inc (2018 - 2021)\n- Built custom Grafana dashboards and Prometheus alert manager rules for latency metrics."),
            ("Education", "B.S. in Computer Science - University of Washington")
        ]
    )

    # =========================================================================
    # 42. Violet Evergarden (TXT) - QA Automation & Test Infrastructure Lead
    # =========================================================================
    violet_content = """Violet Evergarden - QA Automation & Test Infrastructure Lead
==================================================
Contact: violet.evergarden@qatech.io | (555) 056-1122 | Austin, TX

SUMMARY:
QA Automation Lead with 5 years experience designing end-to-end automated testing frameworks using Python, PyTest, Selenium, Playwright, Cypress, and CI/CD pipelines.

TECHNICAL SKILLS:
- Automation Frameworks: PyTest, Selenium WebDriver, Playwright, Cypress, Postman, JMeter
- Programming & DevOps: Python, JavaScript, SQL, Git, Jenkins, GitHub Actions, Docker

WORK EXPERIENCE:
QA Automation Lead | TestCore Solutions (2021 - Present)
- Designed Python PyTest automation framework running 500+ parallel E2E tests in GitHub Actions.
- Increased test coverage from 40% to 92%, detecting critical regression bugs before release.

QA Engineer | WebSoft Systems (2019 - 2021)
- Automated REST API contract tests using Postman and Python requests.

EDUCATION:
B.S. in Software Engineering - UT Austin
"""
    create_txt_resume("resume_violet_evergarden.txt", violet_content)

    # =========================================================================
    # 43. Winston Churchill (PDF) - Cloud Security & IAM Architect
    # =========================================================================
    create_pdf_resume(
        "resume_winston_churchill.pdf",
        "Winston Churchill - Cloud Security & IAM Architect",
        [
            ("Contact", "Email: winston.churchill@seccloud.org | Phone: (555) 057-2233 | Location: Washington, DC"),
            ("Summary", "Cloud Security Architect with 8 years experience designing Zero Trust identity frameworks, AWS IAM policies, cloud security compliance (SOC 2, HIPAA), and Terraform security automation."),
            ("Technical Skills", "Cloud Security: AWS IAM, AWS GuardDuty, SecurityHub, Okta, Zero Trust, Key Management (KMS)\nAutomation & Languages: Terraform, Python, Bash, Docker, Kubernetes Security, CIS Benchmarks"),
            ("Work Experience", "Principal Cloud Security Architect - SecureCloud Inc (2020 - Present)\n- Architected Zero Trust architecture and AWS IAM least-privilege policies across 100+ AWS cloud accounts.\n- Automated compliance scanning with custom Python scripts, ensuring continuous SOC 2 readiness.\n\nSecurity Engineer - GovSec Defense (2016 - 2020)\n- Conducted security architecture reviews and hardened cloud infrastructure against attacks."),
            ("Certifications", "AWS Certified Security - Specialty | CISSP | CCSP")
        ]
    )

    # =========================================================================
    # 44. Xena Warrior (DOCX) - Frontend UI/UX Developer
    # =========================================================================
    create_docx_resume(
        "resume_xena_warrior.docx",
        "Xena Warrior - Frontend UI/UX Developer",
        [
            ("Contact", "Email: xena.warrior@frontendart.io | Phone: (555) 058-3344 | Location: San Francisco, CA"),
            ("Summary", "Frontend Developer with 3 years experience building interactive web user interfaces using Vue.js, React, TypeScript, Tailwind CSS, HTML5, and Figma design translations."),
            ("Technical Skills", "Frontend Stack: Vue.js, Nuxt.js, React, TypeScript, JavaScript, Tailwind CSS, HTML5, CSS3, SCSS\nTools & Workflow: Figma, Vite, Webpack, Git, Storybook, Jest"),
            ("Work Experience", "Frontend Developer - PixelCraft Studio (2022 - Present)\n- Developed modern responsive single-page applications (SPAs) in Vue.js and TypeScript.\n- Implemented pixel-perfect UI components directly from Figma design files using Tailwind CSS.\n\nUI Developer - WebVibe Media (2021 - 2022)\n- Created accessible reusable web components compliant with WCAG 2.1 AA standards."),
            ("Education", "B.A. in Digital Arts & Computer Science - UC Santa Cruz")
        ]
    )

    # =========================================================================
    # 45. Yusuf Pathan (TXT) - Data Analyst & BI Developer
    # =========================================================================
    yusuf_content = """Yusuf Pathan - Mid-Level Data Analyst & BI Developer
==================================================
Contact: yusuf.pathan@analytics.dev | (555) 059-4455 | Chicago, IL

SUMMARY:
Data Analyst with 3 years experience conducting business data analytics, building Tableau & PowerBI dashboards, writing SQL queries, and processing data in Python with Pandas.

TECHNICAL SKILLS:
- Analytics & Dashboards: Tableau, PowerBI, Excel (VBA, Pivot Tables), Google Looker Studio
- Data & Languages: SQL, Python, Pandas, NumPy, PostgreSQL, MySQL

WORK EXPERIENCE:
Data Analyst | Retail BI Systems (2022 - Present)
- Created executive Tableau dashboards tracking daily sales KPIs across 200+ retail stores.
- Automated weekly data extraction and report generation using Python and SQL.

Junior Business Analyst | Insights Group (2021 - 2022)
- Analyzed customer transaction datasets to identify purchasing trends.

EDUCATION:
B.S. in Business Analytics - DePaul University
"""
    create_txt_resume("resume_yusuf_pathan.txt", yusuf_content)

    # =========================================================================
    # 46. Zoe Saldana (PDF) - Senior MLOps Engineer
    # =========================================================================
    create_pdf_resume(
        "resume_zoe_saldana.pdf",
        "Zoe Saldana - Senior MLOps Engineer",
        [
            ("Contact", "Email: zoe.saldana@mlops.io | Phone: (555) 060-5566 | Location: San Jose, CA"),
            ("Summary", "Senior MLOps Engineer with 5 years experience building automated ML training and deployment pipelines using Kubeflow, MLflow, Triton Inference Server, PyTorch, Docker, and Kubernetes."),
            ("Technical Skills", "MLOps & CI/CD: Kubeflow, MLflow, Triton Inference Server, Weights & Biases, DVC, Airflow\nCloud & Compute: Kubernetes, Docker, PyTorch, Python, C++, AWS EKS, CUDA"),
            ("Work Experience", "Senior MLOps Engineer - AI Pipeline Solutions (2021 - Present)\n- Automated end-to-end model retraining and deployment pipeline on Kubernetes using Kubeflow and MLflow.\n- Converted PyTorch models to ONNX and deployed on Triton Inference Server, reducing latency by 50%.\n\nML Infrastructure Engineer - DeepScale Inc (2019 - 2021)\n- Built containerized model training infrastructure on AWS GPU clusters."),
            ("Education", "M.S. in Computer Science - Stanford University")
        ]
    )

    # =========================================================================
    # 47. Arthur Pendragon (DOCX) - Blockchain & Smart Contract Developer
    # =========================================================================
    create_docx_resume(
        "resume_arthur_pendragon.docx",
        "Arthur Pendragon - Blockchain & Smart Contract Developer",
        [
            ("Contact", "Email: arthur.pendragon@web3dev.io | Phone: (555) 061-6677 | Location: New York, NY"),
            ("Summary", "Blockchain Engineer with 4 years experience writing secure Ethereum smart contracts in Solidity, Rust, and Go using Web3.js, Hardhat, and Foundry."),
            ("Technical Skills", "Blockchain: Solidity, Rust, Go, Ethereum, EVM, Smart Contracts, Hardhat, Foundry, Web3.js, Ethers.js\nGeneral: Python, C++, PostgreSQL, Git, Docker"),
            ("Work Experience", "Lead Smart Contract Engineer - DeFi Protocol Labs (2022 - Present)\n- Architected and deployed DeFi liquidity pool smart contracts in Solidity handling $50M+ TVL.\n- Conducted smart contract security audits and gas optimization, saving 25% in execution fees.\n\nBlockchain Developer - CryptoTech (2020 - 2022)\n- Built decentralized application (dApp) frontend integrations using React and Web3.js."),
            ("Education", "B.S. in Computer Science - Columbia University")
        ]
    )

    # =========================================================================
    # 48. Beatrix Kiddo (TXT) - Linux Kernel & Low-Level Systems Programmer
    # =========================================================================
    beatrix_content = """Beatrix Kiddo - Linux Kernel & Low-Level Systems Programmer
==================================================
Contact: beatrix.kiddo@kernel-dev.org | (555) 062-7788 | Seattle, WA

SUMMARY:
Low-level Systems Engineer with 7 years experience developing Linux kernel modules, eBPF network tracing tools, device drivers, and system call optimizations in C and Assembly.

TECHNICAL SKILLS:
- Systems Programming: C, Assembly (x86_64, ARM64), C++, Python, Bash
- Kernel & Low-Level: Linux Kernel Internals, eBPF, Device Drivers, GDB, Valgrind, perf, QEMU

WORK EXPERIENCE:
Principal Systems Engineer | OS Tech Labs (2020 - Present)
- Developed custom eBPF kernel network filters reducing packet processing latency by 35%.
- Authored upstream patches for Linux kernel network subsystem.

Systems Developer | Hardware Core Inc (2017 - 2020)
- Wrote PCIe device drivers in C for high-speed hardware accelerators.

EDUCATION:
B.S. in Computer Engineering - University of Washington
"""
    create_txt_resume("resume_beatrix_kiddo.txt", beatrix_content)

    # =========================================================================
    # 49. Christopher Nolan (PDF) - Computer Vision Engineer
    # =========================================================================
    create_pdf_resume(
        "resume_christopher_nolan.pdf",
        "Christopher Nolan - Computer Vision & Deep Learning Engineer",
        [
            ("Contact", "Email: christopher.nolan@visiontech.ai | Phone: (555) 063-8899 | Location: San Francisco, CA"),
            ("Summary", "Computer Vision Engineer with 4 years experience developing real-time object detection, video analytics, and 3D perception models using OpenCV, PyTorch, YOLO, and TensorRT."),
            ("Technical Skills", "Computer Vision: OpenCV, PyTorch, YOLOv8, TensorRT, ONNX, C++, Python, CUDA\nDomains: Object Tracking, Image Segmentation, Edge AI Deployment, Camera Calibration"),
            ("Work Experience", "Computer Vision Engineer - VisionScale AI (2022 - Present)\n- Developed real-time object tracking algorithms in C++ and OpenCV deployed on embedded camera nodes.\n- Optimized PyTorch YOLO models using TensorRT for 60 FPS video processing.\n\nAI Engineer - Autonomous Labs (2020 - 2022)\n- Trained image segmentation models for autonomous vehicle perception pipelines."),
            ("Education", "M.S. in Computer Vision - Carnegie Mellon University")
        ]
    )

    # =========================================================================
    # 50. Dominic Toretto (DOCX) - Autonomous Systems & ROS Engineer
    # =========================================================================
    create_docx_resume(
        "resume_dominic_toretto.docx",
        "Dominic Toretto - Autonomous Systems & ROS Engineer",
        [
            ("Contact", "Email: dominic.toretto@robotics.dev | Phone: (555) 064-9900 | Location: Detroit, MI"),
            ("Summary", "Robotics Engineer with 5 years experience developing autonomous navigation, Lidar SLAM, trajectory planning, and ROS/ROS2 control nodes in C++ and Python."),
            ("Technical Skills", "Robotics & Simulation: ROS, ROS2, Gazebo, RViz, MoveIt, Nav2, Lidar SLAM, Motion Planning\nProgramming & Control: C++, Python, Kinematics, Control Systems, Git, Linux"),
            ("Work Experience", "Lead Autonomous Systems Engineer - RoboDrive Dynamics (2021 - Present)\n- Developed ROS2 navigation nodes in C++ for autonomous warehouse mobile robots.\n- Implemented Lidar SLAM map building and sensor fusion algorithms for precise localization.\n\nRobotics Engineer - AutoTech Systems (2019 - 2021)\n- Built Gazebo simulation environments for testing vehicle trajectory planning algorithms."),
            ("Education", "B.S. in Robotics Engineering - University of Michigan")
        ]
    )

    print("\n[SUCCESS] Generated 50 sample resume files in './resumes/' folder!")


if __name__ == "__main__":
    main()

