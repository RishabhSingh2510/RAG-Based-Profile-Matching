"""
create_sample_jds.py - Generate 10 Diverse Job Descriptions

Generates 10 realistic, diverse Job Description (JD) text files in `./job_descriptions/`.
These JDs span various engineering domains, experience thresholds (1 to 6+ years),
required skill sets, and preferred qualification blocks to thoroughly test RAG matching,
hard constraint filtering, hybrid retrieval, and scoring performance.
"""

from pathlib import Path

JDS_DIR = Path("job_descriptions")


def create_jd(filename: str, content: str):
    filepath = JDS_DIR / filename
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"[Created JD] {filepath}")


def main():
    JDS_DIR.mkdir(parents=True, exist_ok=True)
    print("Generating 10 diverse sample job descriptions in './job_descriptions/' folder...\n")

    # 1. Senior AI & LLM Systems Engineer
    create_jd(
        "jd_01_senior_ai_systems_engineer.txt",
        """Title: Senior AI & LLM Systems Engineer
Location: San Francisco, CA (Hybrid)
Experience: 5+ years of experience

Job Summary:
We are seeking a Senior AI Systems Engineer to build production-grade Retrieval-Augmented Generation (RAG) pipelines, autonomous LLM agents, and high-throughput vector search services.

Required Skills:
- Python
- FastAPI
- LangChain
- Pinecone
- PyTorch
- Docker

Preferred Skills:
- Kubernetes
- ChromaDB
- LlamaIndex
- AWS

Key Responsibilities:
- Design section-aware chunking and hybrid retrieval architectures using Pinecone and dense vector embeddings.
- Build resilient microservices with Python and FastAPI handling high query traffic under low latency constraints.
- Collaborate with MLOps team to deploy and monitor LLM agent tools in production.
"""
    )

    # 2. Lead Frontend Web Developer
    create_jd(
        "jd_02_lead_frontend_developer.txt",
        """Title: Lead Frontend Web Developer
Location: Seattle, WA (Remote)
Experience: 4+ years of experience

Job Summary:
Looking for a Lead Frontend Engineer to architect next-generation user interfaces for enterprise cloud dashboards using modern web frameworks.

Required Skills:
- React
- TypeScript
- Next.js
- Tailwind CSS

Preferred Skills:
- Vue.js
- GraphQL
- Node.js
- Figma

Key Responsibilities:
- Lead the architecture of React and Next.js single-page applications with server-side rendering (SSR).
- Optimize bundle size and web vitals performance across desktop and mobile devices.
- Collaborate with designers to translate Figma mockups into accessible HTML5/CSS3 components.
"""
    )

    # 3. Senior Cloud DevOps & Infrastructure Architect
    create_jd(
        "jd_03_cloud_devops_architect.txt",
        """Title: Senior Cloud DevOps & Infrastructure Architect
Location: Austin, TX (Onsite)
Experience: 6+ years of experience

Job Summary:
We require a Senior DevOps Architect to automate multi-cloud infrastructure provisioning, manage container orchestration platforms, and enforce CI/CD pipeline security.

Required Skills:
- AWS
- Kubernetes
- Terraform
- Docker
- CI/CD

Preferred Skills:
- Ansible
- Python
- Go
- GCP

Key Responsibilities:
- Provision modular AWS and GCP cloud infrastructure using Terraform and Ansible.
- Manage enterprise Kubernetes (EKS) clusters, Helm releases, and GitOps deployments with ArgoCD.
- Build automated GitHub Actions and Jenkins CI/CD pipelines with zero-downtime deployment strategies.
"""
    )

    # 4. Senior Data Engineer & Pipeline Architect
    create_jd(
        "jd_04_data_pipeline_architect.txt",
        """Title: Senior Data Engineer & Pipeline Architect
Location: Chicago, IL (Hybrid)
Experience: 5+ years of experience

Job Summary:
Join our analytics core team to construct scalable big data ETL pipelines and high-performance cloud data warehouses.

Required Skills:
- PySpark
- Snowflake
- Apache Airflow
- Python
- SQL

Preferred Skills:
- dbt
- Databricks
- Kafka
- Scala

Key Responsibilities:
- Build PySpark data processing workflows ingesting terabytes of raw unstructured event data.
- Orchestrate data DAGs using Apache Airflow for automated loading into Snowflake data warehouses.
- Optimize SQL queries, data partitioning, and dbt models for high-speed business intelligence queries.
"""
    )

    # 5. Embedded Systems & Firmware Specialist
    create_jd(
        "jd_05_embedded_firmware_engineer.txt",
        """Title: Embedded Systems & Firmware Specialist
Location: San Jose, CA (Onsite)
Experience: 3+ years of experience

Job Summary:
Seeking an Embedded Systems Engineer to write real-time micro-controller firmware and low-level peripheral drivers for next-gen IoT hardware nodes.

Required Skills:
- C++
- C
- FreeRTOS
- Embedded Linux
- STM32

Preferred Skills:
- CAN bus
- I2C
- Python
- UART

Key Responsibilities:
- Develop deterministic C/C++ firmware on STM32 microcontrollers using FreeRTOS kernels.
- Write device drivers for SPI, I2C, and UART sensor interfaces.
- Perform hardware debugging using oscilloscopes, logic analyzers, and GDB.
"""
    )

    # 6. Lead Cybersecurity & Incident Response Engineer
    create_jd(
        "jd_06_cybersecurity_lead.txt",
        """Title: Lead Cybersecurity & Incident Response Engineer
Location: Washington, DC (Hybrid)
Experience: 5+ years of experience

Job Summary:
We need a Lead Security Engineer to oversee penetration testing, threat detection monitoring, SIEM log analysis, and incident response operations.

Required Skills:
- Penetration Testing
- Python
- Network Security
- Splunk
- SIEM

Preferred Skills:
- CISSP
- Wireshark
- Burp Suite
- Nmap

Key Responsibilities:
- Execute penetration testing across web applications, API endpoints, and internal network infrastructure.
- Monitor SIEM telemetry feeds using Splunk to detect and mitigate malicious activity.
- Automate security auditing and vulnerability scanning using custom Python scripts.
"""
    )

    # 7. Lead Cross-Platform Mobile App Engineer
    create_jd(
        "jd_07_mobile_app_developer.txt",
        """Title: Lead Cross-Platform Mobile App Engineer
Location: Los Angeles, CA (Remote)
Experience: 3+ years of experience

Job Summary:
Looking for a Mobile App Developer to build sleek, high-performing mobile applications for iOS and Android devices.

Required Skills:
- Flutter
- React Native
- Swift
- Kotlin
- Firebase

Preferred Skills:
- Fastlane
- Supabase
- GraphQL
- SQLite

Key Responsibilities:
- Architect cross-platform mobile apps using Flutter and React Native connecting to Firebase backends.
- Write native Swift (iOS) and Kotlin (Android) modules when deep hardware integration is required.
- Set up automated mobile app build and release pipelines using Fastlane.
"""
    )

    # 8. Junior/Mid-level Python Backend Developer
    create_jd(
        "jd_08_junior_python_backend_developer.txt",
        """Title: Junior/Mid-level Python Backend Developer
Location: Denver, CO (Hybrid)
Experience: 1+ years of experience

Job Summary:
Seeking a motivated Python Backend Developer to construct clean, well-tested REST APIs and backend web services.

Required Skills:
- Python
- FastAPI
- Django
- REST APIs
- PostgreSQL

Preferred Skills:
- Docker
- PyTest
- SQLite
- Git

Key Responsibilities:
- Implement scalable REST API endpoints using Python, FastAPI, and Django.
- Manage relational database migrations and write efficient PostgreSQL queries.
- Write unit and integration tests using PyTest to ensure application stability.
"""
    )

    # 9. Senior NLP Research Scientist
    create_jd(
        "jd_09_nlp_research_scientist.txt",
        """Title: Senior NLP Research Scientist
Location: Boston, MA (Hybrid)
Experience: 4+ years of experience

Job Summary:
Looking for an NLP Research Scientist to fine-tune transformer models, design custom Named Entity Recognition (NER) systems, and optimize text embeddings.

Required Skills:
- PyTorch
- Hugging Face
- Transformers
- BERT
- NLP
- Python

Preferred Skills:
- SpaCy
- CUDA
- FastText
- NLTK

Key Responsibilities:
- Train and fine-tune state-of-the-art transformer models (BERT, LLaMA) for domain-specific NLP tasks.
- Build custom tokenization, entity extraction, and sentiment analysis pipelines.
- Publish research findings and benchmark model accuracy across evaluation datasets.
"""
    )

    # 10. Senior Database Administrator & Storage Engineer
    create_jd(
        "jd_10_database_admin_engineer.txt",
        """Title: Senior Database Administrator & Storage Engineer
Location: Dallas, TX (Onsite)
Experience: 6+ years of experience

Job Summary:
Seeking a Senior DBA to manage enterprise database infrastructure, tune high-throughput SQL queries, and implement failover replication.

Required Skills:
- PostgreSQL
- MongoDB
- Redis
- Query Performance Tuning
- Replication

Preferred Skills:
- Apache Cassandra
- Python
- Bash
- Ansible

Key Responsibilities:
- Administer production-grade PostgreSQL, MongoDB, and Redis clusters under heavy transaction loads.
- Diagnose and eliminate slow query execution plans through index optimization and parameter tuning.
- Design automated backup, point-in-time recovery (PITR), and active-passive streaming replication.
"""
    )

    print("\n[SUCCESS] Generated 10 sample job descriptions in './job_descriptions/' folder!")


if __name__ == "__main__":
    main()
