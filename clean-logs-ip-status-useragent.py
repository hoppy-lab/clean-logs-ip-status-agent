import streamlit as st
import pandas as pd
import re
import io

def parse_log(lines):
    data = {"ip": [], "status_code": [], "user_agent": []}
    
    ip_pattern = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
    status_pattern = re.compile(r"\b\d{3}\b")
    quoted_pattern = re.compile(r'"(.*?)"')  # capture tout entre guillemets

    for line in lines:
        # IP
        ip_match = ip_pattern.search(line)
        ip = ip_match.group(0) if ip_match else None

        # Status code (premier token de 3 chiffres après l'IP)
        status_code = None
        for match in status_pattern.finditer(line):
            if ip and match.start() > ip_match.end():
                status_code = match.group(0)
                break

        # User-Agent : dernière chaîne entre guillemets
        quoted_matches = quoted_pattern.findall(line)
        user_agent = quoted_matches[-1] if quoted_matches else None

        if ip and status_code and user_agent:
            data["ip"].append(ip)
            data["status_code"].append(status_code)
            data["user_agent"].append(user_agent)

    return pd.DataFrame(data)

def main():
    st.title("Analyseur de Logs Serveur")

    uploaded_file = st.file_uploader("Choisissez un fichier de logs", type=["log", "txt", "csv"])
    
    if uploaded_file is not None:
        lines = uploaded_file.getvalue().decode("utf-8", errors="ignore").splitlines()

        if not lines:
            st.error("Le fichier est vide.")
            return

        # Parsing
        df = parse_log(lines)
        st.dataframe(df)

        # Téléchargement CSV avec tabulation
        if not df.empty:
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False, sep="\t")
            st.download_button(
                label="Télécharger le fichier CSV (séparateur tabulation)",
                data=csv_buffer.getvalue(),
                file_name="logs_extraits.csv",
                mime="text/csv"
            )
        else:
            st.warning("Aucune donnée exploitable trouvée.")

if __name__ == "__main__":
    main()

