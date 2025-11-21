import ollama
import prompts  # 先ほど作成したprompts.pyをインポート

# Ollamaで使用するモデル名
# 実行前に `ollama pull hf.co/mmnga/Llama-3.1-Swallow-8B-Instruct-v0.5-gguf` 等でモデルを準備してください
MODEL_NAME = "hf.co/mmnga/Llama-3.1-Swallow-8B-Instruct-v0.5-gguf"

def evaluate_communication(before_response, userinput1, response1, log):
    """
    3つの観点でコミュニケーションを評価する関数
    """
    
    # 評価項目の定義（名前とプロンプトテンプレートのペア）
    evaluation_criteria = {
        "1. 回答の的確性": prompts.prompt_relevance,
        "2. 論理性・わかりやすさ": prompts.prompt_clarity,
        "3. 態度・協調性": prompts.prompt_attitude
    }
    
    results = {}

    print(f"--- 評価開始 (Model: {MODEL_NAME}) ---")

    for criteria_name, prompt_template in evaluation_criteria.items():
        # プロンプトに変数を埋め込む
        formatted_prompt = prompt_template.format(
            before_response=before_response,
            userinput1=userinput1,
            response1=response1,
            log=log
        )

        try:
            # Ollamaに問い合わせ
            response = ollama.generate(
                model=MODEL_NAME,
                prompt=formatted_prompt,
                options={
                    "temperature": 0.0, # 評価の一貫性のためランダム性を排除
                }
            )
            
            # 応答からスコアを取得（余分な空白などを除去）
            score = response['response'].strip()
            results[criteria_name] = score
            print(f"{criteria_name}: {score}")

        except Exception as e:
            print(f"Error evaluating {criteria_name}: {e}")
            results[criteria_name] = "Error"

    print("--- 評価終了 ---")
    return results

if __name__ == "__main__":
    # テスト用データ
    sample_before_response = "プロジェクトの進捗はどうですか？遅れの原因があれば教えてください。"
    
    sample_userinput1 = "すいません、ちょっと遅れてます。でもまあなんとかなると思います。"
    
    sample_response1 = "遅れていることは把握しました。「なんとかなる」の根拠や、具体的な遅延理由をもう少し詳しく教えていただけますか？"
    
    sample_log = """
    User: こんにちは。
    Mentor: こんにちは。本日はどのような件でしょうか？
    User: プロジェクトの報告です。
    Mentor: わかりました。では、プロジェクトの進捗はどうですか？遅れの原因があれば教えてください。
    """

    # 評価実行
    final_scores = evaluate_communication(
        before_response=sample_before_response,
        userinput1=sample_userinput1,
        response1=sample_response1,
        log=sample_log
    )

    # 結果の表示
    print("\n=== 最終評価結果 ===")
    for k, v in final_scores.items():
        print(f"{k}: {v}")