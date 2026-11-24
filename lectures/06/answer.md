# 第6回 解答

## 演習

<!-- [tool call] の行は、表示された行をそのまま貼り付けてください。終わらなかった STEP は、空欄のままでかまいません。 -->

- STEP 1 のツールの名前：glossary_search_glossary
- STEP 2 の [tool call]：[tool call]   glossary_search_glossary({'query': '3レベル'})
- STEP 3 の [tool call]：[tool call]   fetch_fetch({'url': 'https://modelcontextprotocol.io/'})
- STEP 4 の [tool call]：[tool call]   aws_aws___search_documentation({'search_phrase': 'Amazon S3 バージョニング 概要', 'topics': ['general']})
[tool call]   aws_aws___search_documentation({'search_phrase': 'Versioning what is Amazon S3 versioning', 'topics': ['general']})
- 気づき・疑問：MCPを利用することで、エージェント本体のコードを変更することなく、設定ファイルを通じて外部ツールを追加できることを学んだ。また、ローカルとリモートのMCPサーバーを共通の仕組みで利用できる点が興味深かった。STEP 4では、モデルが日本語で検索した後、自律的に検索クエリを英語に変更して再検索していた。一方、ツールの追加や複数回の呼び出しによって入力トークン数が増加するため、回答精度と処理コストのバランスをどのように最適化するかが課題になると感じた。

## 宿題

<!-- 基礎・実装・発展のどれか1つに取り組めば完了です。 -->

- 取り組んだレベル：基礎
- やったこと：MCPサーバーに講義概要を取得する get_lecture_summary ツールを追加し、モデルが適切にツールを選択・実行できるかを確認した。また、pytestによる動作検証を行った。
- 結果：第2回の学習内容に関する質問に対し、追加したツールが適切に呼び出され、講義資料に基づく回答が生成された。テストでは第5回の演習で変更した RAG_TOP_K = 1 が原因でエラーが発生したが、3に変更することで解消した。
- 気づき・疑問：MCPを利用することで、エージェント本体を変更せずに機能を拡張できることを学んだ。また、過去の設定変更が後続のテストに影響することを経験し、リグレッションテストの重要性や、設定値に依存しないテスト設計の必要性を理解した。今後、利用可能なツールが増加した際に、モデルが適切なツールを選択できるよう、ツールの説明文をどのように設計すべきかにも関心を持った。
