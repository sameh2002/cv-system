from rag.rag_pipeline import index_cvs, ask_question

if __name__ == "__main__":

    # 1. index CVs (à faire une seule fois)
    index_cvs("output/structured_cvs.json")

    # 2. poser question
    ask_question("cherche candidat avec expérience en React")