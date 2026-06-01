# 083 - K-OS Backup and Export Pack Core

Gerado em: 2026-06-01T13:13:37Z

## Objetivo

Criar pacote seguro de backup e exportacao do K-OS com manifesto, indice exportavel sanitizado, evidencias e dashboard somente leitura, sem copiar segredos, sem incluir local_secrets, sem incluir memory/runtime, sem executar recovery, rollback, drill, reset, force push ou limpeza destrutiva.

## Status

- Checkpoint: 083
- Camada: K-OS Core
- Status do pack: healthy
- Checkpoint anterior: 082 - K-OS Command Registry Core
- Proximo checkpoint: 084 - K-OS Release Candidate Gate Core
- Arquivos incluidos no manifesto: 4559
- Arquivos excluidos por politica: 2302
- Conteudo copiado: 0
- Arquivo compactado criado: False
- Referencias sensiveis detectadas: 4

## Contagem por escopo

| Escopo | Quantidade |
|---|---:|
| agent_modules | 11 |
| configuration | 7 |
| content_assets | 2 |
| core_runtime | 2668 |
| documentation | 361 |
| live_runtime_surface | 55 |
| memory_non_runtime | 212 |
| operator_scripts | 10 |
| root_or_misc | 3 |
| sanitized_reports | 660 |
| streamlit_pages | 570 |

## Contagem por extensao

| Extensao | Quantidade |
|---|---:|
| .ai | 2 |
| .baf | 1 |
| .baj | 1 |
| .css | 5 |
| .dat | 1 |
| .db | 2 |
| .db-journal | 2 |
| .diff | 2 |
| .html | 6 |
| .js | 5 |
| .json | 999 |
| .jsonl | 123 |
| .landing | 1 |
| .lock | 2 |
| .log | 36 |
| .md | 556 |
| .pb | 1 |
| .pma | 1 |
| .png | 8 |
| .ps1 | 27 |
| .py | 2338 |
| .sql | 1 |
| .txt | 7 |
| [none] | 432 |

## Raizes avaliadas

| Raiz | Existe | Status | Incluidos | Excluidos |
|---|---|---|---:|---:|
| README.md | True | found | 1 | 0 |
| requirements.txt | True | found | 1 | 0 |
| .gitignore | True | found | 1 | 0 |
| app.py | True | found | 1 | 0 |
| streamlit_app.py | False | missing | 0 | 0 |
| Home.py | False | missing | 0 | 0 |
| k_atlas | True | found | 2668 | 1728 |
| agents | True | found | 11 | 11 |
| live | True | found | 59 | 0 |
| memory | True | found | 215 | 0 |
| reports | True | found | 940 | 3 |
| campaigns | False | missing | 0 | 0 |
| content_packs | True | found | 7 | 0 |
| configs | True | found | 7 | 0 |
| scripts | True | found | 10 | 0 |
| pages | True | found | 570 | 560 |
| docs | True | found | 68 | 0 |

## Escopos obrigatorios ausentes

Nenhum escopo obrigatorio ausente.

## Amostra de arquivos manifestados

| Escopo | Caminho | Tamanho | SHA256 |
|---|---|---:|---|
| documentation | README.md | 4245 | 17a5f6848b04350d8bf89f502d6673a73b420599b0169629379fb36c23897f5e |
| root_or_misc | requirements.txt | 639 | 1ace6f394fcaf9febbbbe13ba7b1447e2ad5dff3eeebb38fad14ea306e957a04 |
| root_or_misc | .gitignore | 14617 | 76de066817e4860e346918162113595d47b94b0e3571bf11afe5338857d63d02 |
| root_or_misc | app.py | 20441 | 8e245790016a880d091b79c2f4f1293600483a00f180a24bad0a0f9bcd511186 |
| core_runtime | k_atlas/__init__.py | 54 | be812977efa949564e92d04caf888991ecb5db2ee017207f3d86669fec05b85f |
| core_runtime | k_atlas/agents/commercial_brain.py | 4065 | dc39d040082b6ba5ab2e454d2e42bbb1b26eda78aff01b69da09f97d10592b44 |
| core_runtime | k_atlas/agents/commercial_orchestrator.py | 3218 | 6435f992302f80f9fe3d5b0e2e7e14a5038c0c59c2822d40395cdb3a15b5d523 |
| core_runtime | k_atlas/agents/decision_engine.py | 2465 | 8fbfc6d7453d75df8ab24387575165525102d2b76c684ce248dfd6c8a588ed9d |
| core_runtime | k_atlas/agents/instagram_content_pack.py | 3669 | bef2bf404a25576e8d8f65341cb29413c6de4029f555956bf3fd46a18e3d50ab |
| core_runtime | k_atlas/agents/marketing_manager.py | 5594 | 4db73f1c391a186b4544819eb287fdc1bf9469f727c13812064e0a5ce154943f |
| core_runtime | k_atlas/agents/publisher_instagram.py | 2221 | e0adafcf491a4f7d951348c808c37b433e33352f46e2b69e0d03b7791fa24f51 |
| core_runtime | k_atlas/approved_campaigns/approved_20260528_091253.json | 1396 | 9398fc90eb889d0712fb1801f3a2a9869a4799c5138c68b9e5c33d5728c19e59 |
| core_runtime | k_atlas/browser/instagram_profile/BrowserMetrics-spare.pma | 4194304 | bb9f8df61474d25e71fa00722318cd387396ca1736605e1248821cc0de3d3af8 |
| core_runtime | k_atlas/browser/instagram_profile/Crashpad/settings.dat | 40 | 3ab950749506ad795c1545643a5dfe92d19ec1f43e0aa135e0cae3c4fea9d4dd |
| core_runtime | k_atlas/browser/instagram_profile/Default/Account Web Data | 77824 | cba5dc747c82700f95dcd4408352f8e08340311fd52a72b064f5e78280513e25 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Account Web Data-journal | 0 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Affiliation Database | 86016 | a3fce4a52ef8c2314f50b1ebfa729488ea906e0836307cf13b8af67c0b814afc |
| core_runtime | k_atlas/browser/instagram_profile/Default/Affiliation Database-journal | 0 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| core_runtime | k_atlas/browser/instagram_profile/Default/AutofillAiModelCache/LOCK | 0 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| core_runtime | k_atlas/browser/instagram_profile/Default/AutofillAiModelCache/LOG | 0 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| core_runtime | k_atlas/browser/instagram_profile/Default/AutofillStrikeDatabase/LOCK | 0 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| core_runtime | k_atlas/browser/instagram_profile/Default/AutofillStrikeDatabase/LOG | 0 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| core_runtime | k_atlas/browser/instagram_profile/Default/BookmarkMergedSurfaceOrdering | 6 | 4489f9e3e454748b3521eb214e0a5694d562cff3d9ff511cb456953c8f534c00 |
| core_runtime | k_atlas/browser/instagram_profile/Default/BudgetDatabase/LOCK | 0 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| core_runtime | k_atlas/browser/instagram_profile/Default/BudgetDatabase/LOG | 0 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/data_0 | 45056 | 1c144d063f924c2d0c00a476cde89c67b179be01e82558382a6ed1211f0f040a |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/data_1 | 270336 | b7276220d935403675d6fe4574b57906ce8cf4c72b6554940a9da88155c6b2f4 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/data_2 | 1056768 | c0e10da732d2bb4b10cf80ed39202177484d6446f6512e2b0ec1b6d4833208a4 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/data_3 | 4202496 | 67df7744e2d17b6c467f2703fa07f9f4e4287cf99008801f850d2ac3918a6942 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000001 | 155129 | b2702f679595b1a4e8746a6129deeb2de8a9e54b3949f19c1f6407ef1513776d |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000002 | 75179 | f608f218c648cb4005162ae6bb36192ad6654317fbf41eb7a9abd7accd3617fe |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000003 | 218447 | f53c32f65be15feddfac4905bbcf3369b4a4489bb10f02c91af19e8fda9ab896 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000004 | 856273 | 7abc7f37908f3ca5ad683d05b926e5b6ad109688590126388a8ffecc247c27c3 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000005 | 16973 | 095875be7c3550d803135b16111bc9b6e42804b02c9fb9dd105eea7150686994 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000006 | 36559 | c1340b6614dba7305faeabb69a51da4b4ae1c3e0c37f16c23fe0dc0f2a1b8990 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000007 | 31735 | e23dfaa8997d4850f254fa05a285c02da754802a7840b7a688ecfcd5a4cddfba |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000008 | 195285 | 636a6702b995497425a033f601c76fcee290c25a6eb4205b59e25c258f6a70bd |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000009 | 565818 | 94a749dbefd9b52ad0abbb703bb95e6670cebe373b98ff263e4ece67217809e6 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00000a | 33192 | 89f2a1081d32a905dc37cf8ecbede5eab96c4a2b94b405e85633960fc2def465 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00000b | 183220 | 0dce730051c3b1526526743fc0079505bdf5454b79f6ec1c1fb2a7cb26350694 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00000c | 94598 | 30341f614cced83e444115fb02077509b57b44c801765eabe10b3d5451baac01 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00000d | 36701 | 5494e5038e42eb508eaeedb3be37f2d2574374cec0ec8a22a2d0014b254ac221 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00000e | 17632 | 171abb8f3fc1c7f745e9d1be339348a8714fd776cc018ad6edac0d80b862406b |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00000f | 23743 | 869106254a6192d92e71c764b82cb9b19596b8e22e6fbc77aa5bbfb33fbd46a9 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000010 | 78659 | 5c4e3799d70c600b55b2b4d8e6f7dfa87de51e245c94660e74b9a72690a662d0 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000011 | 137980 | 73c6f9c53ad51d9f3ef4a9b5bd2ec1ad8f46c6739987e5a7b02ced2f90a681bb |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000012 | 18696 | 4aa317e28348c9e32054fdd647520d3d4cc75fff0f2072454d62570377c7bb1c |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000013 | 59632 | 6dff696e6856cc4b8adada98019b4c6bc461667d22bce068184d92c78857c5f9 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000014 | 17295 | a4dd47501ccf9931a70702b8392f58b0d1bd1a5411d9b74b8b627d7ca6f03e5e |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000015 | 157015 | 31420d962b800165dba6873b86d577b51afcb8062af46d07ff95b9161845196d |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000016 | 75131 | bba53b9931cc32468efc01836e6d276cd91a7134f81871dce341fbbc09337ef4 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000017 | 252194 | c5b16f4cd95e57f37d56106ada7fa24a3bb26c67f28aafba958cfa6384af2a99 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000018 | 936167 | 45daa5c4014d7050cc130d7d017d9f39626c5487b71c0805639a808c7712b6e7 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000019 | 33694 | fda503e3d7d3e848bcc8a7eafe645308607ce707ca1c5d724a8cd3894b0417fc |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00001a | 79996 | 2c87fa01c09b9c70058debf0051ea5195ae3595b5b064f14f3c95b8b10ad35c9 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00001b | 17322 | 8415b297f78b7ad939bfd0d7ae2b43b7f09a9285fe56a38f0fb4e01e70ff936e |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00001c | 18872 | 1a8c52a08a05b52c76ba9e24614e7637bc09ef107781a706309809d10aa2e45d |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00001d | 30624 | f84946f8f0466f91d0af47736caab01fea4fe20a642d7a85f8ef162feecdc7dd |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00001e | 36179 | 8bbad1dba38199058c4a7e22c2a1d1f979ae4016b8b64c573584ca397b5c109c |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00001f | 106991 | a2166ebb8f480585c17ac9027f8acc21a4fb403b6264a6bf3e7372456c7c6cb0 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000020 | 370796 | f1193cec1171a48dff98bf9ad9ab580f5cece304ddd192b4ed84550b3d213d10 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000021 | 202857 | 8fffa513cfddac354823177b0456deb8a419617becb49588aebe23781ac01c46 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000022 | 60793 | 1436a28992217c80d302ad85837a7dba86466b883f328bda93cd8964083b437a |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000023 | 58410 | df77e7c4fe0611125ed4f6896f5381fefe7f6d4078bc87fcb9678c486272b8ea |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000024 | 78659 | 5c4e3799d70c600b55b2b4d8e6f7dfa87de51e245c94660e74b9a72690a662d0 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000025 | 122474 | 2c104999f7fa08a4e46de2362054b353330df619952a70ce2c0b1ed551c76ea0 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000026 | 79857 | c03d2e37604f29123730539ad6e727515da3a6ab3f884eb507d1e74dacc198d8 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000027 | 36903 | edbbb0e6106787e03cd62fbad048d914d990b7bdecb679f7bad4bbdb010e0b45 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000028 | 162724 | 25ff67f9a93d732f34589ab8fa0a6a62ac7e7011d3b9be400489b531f6921180 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000029 | 122234 | fc527e725538d8030d886dc90db54f0d51d2d66c0bacaf6d9f35b999551db3f9 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00002a | 955263 | 129173cd9ad1b6c2208a233d983fd768627e9c7bba78c959938dfe891eb44599 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00002b | 25328 | 7514fa72ac89701245353ad915da854ffb8964c517c1c94ddbc7c528db14906f |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00002c | 332437 | 7e44414746ec95e30cced7793918f97072b3e541d1717cf043464c99f2c7e11d |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00002d | 79819 | 796021194a34e8dbd870f73b8173aa8767f374fc44240ee64826f28814854805 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00002e | 547876 | 245faf18c30a0d3019654ad30f22138980c5f6e0f2bce9c16e425f67b7478a34 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00002f | 36607 | 96876cf83c6c3ecdeaa95b6326cde2a33c330d41f6a154c3478290e1efa327b5 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000030 | 17434 | e39c8f338314fd0919c54e3ff46e5a935414c9e298cafdb09bcc6490c0256658 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000031 | 23465 | 8f2b9e7c6a6a64ec19183e1d18fa7dd9a70cec8ddbe751be719e7752004589b0 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000032 | 16645 | 01d0461285c8a0e888f412ad0e1779461ec17ca2bc5e432dfd90e1dedb9da36b |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000033 | 20846 | 70cb744bf140a6b2b94fc00562c7b674827ba9da0565464edb8744ef0924d7c8 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000034 | 61451 | 78f0979ab87f9b018d2eb25860b0b3918aa22ce6f29606e6465870cb6ff804b7 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000035 | 778304 | 699a48d52bde639ff9f78b27ab5308f159f1210c1a0d6c208d028628a9d2d11e |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000036 | 531309 | 0889b7f804b9d62b0355a7ef4bfbaba4f08acde8dcf4908ef500df6a689e47fc |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000037 | 60101 | 51c2de45f7a37c56aca127777e6edc6f229822addc1351ed89c25e9218c9ed8f |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000038 | 193313 | 92720ceda16b738dd069f9b63c13af6a373f71a762b061ca73e6d8a886eed6bc |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000039 | 80648 | c86679924d69f45ffacd65f8b7722056640f9f3b2c453e92441e6a945254e122 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00003a | 51094 | 8d2f13d80b358923fa2ec7c6b112b714da2644dac3cceb5c5c19ab40d76ed5a2 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00003b | 31283 | 1aae857051b4fd685774c459425efc5cee81cc94801715a0b751eed47d2346a7 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00003c | 42924 | e040c7fdb05b3870abbba137609f805c10d66c618587e1d6e0df2b933902adb8 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00003d | 45178 | 27aab8bf1e14f6ea526940d669e29e3d1562b78c21c290f9285b6b7c66b3ac1f |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00003e | 41469 | 289020494e95f3ebaa7aa0170db7f628a6b346306b38393dbc4830a399c59e9c |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00003f | 77228 | 36da6d5b0874706eaf2191d6ae18aae59e768672ac668e61caaaadd4a81e6455 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000040 | 43855 | 8bc6438237b6388ee3e0d4059217aa948273eca6fd43d02c4fab2bbfc662e6f9 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000041 | 42026 | f578fac56b117dab2b183eeb1e6833db5ed7f143d96cc78342648f33d2f7f8bb |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000042 | 75179 | f608f218c648cb4005162ae6bb36192ad6654317fbf41eb7a9abd7accd3617fe |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000043 | 32604 | 927ed6e861fd3eeb0fa650511d26ee4c8c967b8f884c01b46177d77322ff641d |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000044 | 21758 | 218719a906b5b80f4d783609d2cc0bd9a836b225fd9e0f5cca7eff0e81f7e554 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000045 | 32120 | d9fa82fe0754d1ff3753432189b653d7632aca7a0af78ef1d85ed559112536ef |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000046 | 39548 | aa3bc0dc94636f2199fc9dae96b085bc6c9afad35125b498e34a78564602fbc0 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000047 | 33355 | f63238b2cedbc6e66506d24d723aae4782865998021dc51104d5bfb1307dd628 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000048 | 17159 | df06b7ebb0edf27d2059e7484543ea8b0d0c00855203f828734e349b1af1cccd |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000049 | 1095738 | 1480eab1f5a915d0116393c144a0a9e30fc598803b0812f68255feacd5d0c79b |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00004a | 49745 | 6d75d1d17eaa563bfeb540be40ead0b499ce53fbab816a8e9886c2a8bd453040 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00004b | 17429 | fa03d7d4ccb9dc507b1edd31a0612841406eacf385b74bd9801b3bb7b4508229 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00004c | 18532 | 8cd2cab4c0e9898828e8b49aabf5320988560a611f4790af2a2696d07ff5c797 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00004d | 384288 | 09557747283714a614f0506f2b2ad5ad98167cd92c9551389ff3059d273b5297 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00004e | 851255 | 44c7ab84c57bb068be1f4547b5870052c0d5476d6e37704b6027e3203ad1aba6 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00004f | 1667775 | e5c1b9fdbe98236891e9b42b8626cc87351395fa7562d79f064d41d6f6c3694f |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000050 | 27873 | 502b10935c5bac187f1f8c20e707bf48f99c01cb03538d1ba6fc012fe547872f |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000051 | 31344 | a95f83b7e7d975a0c282b001d1620cb1a0253aa410f467a16bed87d0d84f93b5 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000052 | 560666 | b43521b7b3e5bb1b32c0c8fd56ddedad7a0ea78cb43a8db3240fb118b87eff71 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000053 | 353438 | 16bae1e97d7ef600160592d87f47463e4ecaab1ce686e73d28c2f398e5a139fc |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000054 | 64302 | 4fb1f283de851a1be08635699792b077dfcaa0fd5521df6213fc196e3c373b26 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000055 | 151746 | 6cc835310c2e69a59e40a6edc24838286dd0ca53001c5b29166bd0c2d540cacf |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000056 | 1307789 | 9a60e3628b503c3eaabe6c1f7f1acfe5cc3fd6bb116dea2c74560d2e937c6ea3 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000057 | 19361 | d30c035a7aa733b1daf4331e8e5fb2651ac967bdf20dbd7508060277ae75e564 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000058 | 21332 | 52db9eb28309b4354b05306a69ebb73e84293e5124676fcd3bd5cf1464cfdf27 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000059 | 32905 | fa3ee2a4a7afe5259528d848467929642b255398490a2db8435ae2b3db87c3ff |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00005a | 35366 | b91db4c1a69e83680e46cb119885a34ab1d7d3f79ad5f6e0502bc0e0b241561a |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00005b | 85103 | d74ecbf26cbd856cdb8b49e1779c1ad91959c6ee91f9b74344cba164e5b07d86 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00005c | 29366 | 87848390d934519040b4597614a4fbd87a731cac91116a6de38480517c7d3ce8 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00005d | 61024 | c7dab90238bcd52a9046d80f4fa0e563b1833d6ed0dfe0f5f2a574d90dbfba85 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00005e | 28341 | 2074e9bbc9de308871b54ac09a424ec4761d2d30b59a956d125f21ce1f208772 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_00005f | 132183 | e254e97066b64a6e8d09e03453924431ab6c81c06b0461a456d17202cac052c2 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000060 | 29550 | e2dcee81c8ddf5794b33d9286447c9a86e56e45ecb1785936699fe4b2f860133 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/f_000061 | 115118 | 7269b549ba3d0a2f397f9ece63f5f5a56f13aaa5d31cd32be6ddd6c99a581679 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/Cache_Data/index | 524656 | 5a121ff44507b1beb604c8f5cb4c7c97fb3cea45fd3d4c55c7fb0351761bf7d2 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/No_Vary_Search/journal.baj | 4 | 9c169428d852e25bd59b27652ed533d2a1f09f96e4c329fa5e06f47e16731543 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Cache/No_Vary_Search/snapshot.baf | 77272 | 6915d1a45c11b9e01cb79c200c9e6b0d916b6312ea8b53d01bc58f9d344f6b67 |
| core_runtime | k_atlas/browser/instagram_profile/Default/ClientCertificates/LOCK | 0 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| core_runtime | k_atlas/browser/instagram_profile/Default/ClientCertificates/LOG | 0 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Code Cache/js/0200f65f09784edf_0 | 239 | 664a3531212db4092d1ed28f99946f71802f5713085798d13df52358f15a3dc5 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Code Cache/js/03e0197972d6b1a8_0 | 771 | fb0ec5b0efbe466369676fdaa1c50d03db8c2f2f15c7e28c540216c78c0bf771 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Code Cache/js/046973be717d2056_0 | 248 | 4e56c6f062fa0c17a6ea00b2a702c868f154238038cf512772565a8445e6f690 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Code Cache/js/05143e29ec4f5c0f_0 | 1079 | ae0b80c6e49f2a8e6158b88192982a0cd81c6c6376ca6819ba535ed002fabf5a |
| core_runtime | k_atlas/browser/instagram_profile/Default/Code Cache/js/0d57343cfb7c5f05_0 | 13629 | 687d5eba7f055d913d0ea17daa8bd450bd063f3bbe1053048c5879fbffe295ab |
| core_runtime | k_atlas/browser/instagram_profile/Default/Code Cache/js/0ea325e1bb9d03d0_0 | 1895 | a00f89a329d2d43598b782b335f6e5f62cd5e5d6bab76df2fb443eae7281ac82 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Code Cache/js/113b2b73629329da_0 | 2495 | 411ef1a31f4b27b8aff57fee703953f7f859ebbf1ef1ff05d89f80dcdc1eb495 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Code Cache/js/1228edf3d0f7d106_0 | 235 | 26bf5b349e7e4bd5b088e0d717860be48b3186714d25f4715c72d1262a09a1d3 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Code Cache/js/17497a3f3f321ad8_0 | 230 | df08231d45603b178743592635de2ca1deae53babb678eb3a36a5751ca53ae6b |
| core_runtime | k_atlas/browser/instagram_profile/Default/Code Cache/js/17861682ba7e9603_0 | 248 | 4721a56a6fc7f0299795144eb0be0943e75f765c07c2b9469132056a06c870d9 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Code Cache/js/1bc04656fcf4725e_0 | 3898 | 43f5aa646615bddc41212ea43edcb5d98da163597aa417221c033afff9b41b21 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Code Cache/js/1d56ece9e019f730_0 | 587 | 139e8256a3b598f8fd42758716d1713e62094a929173561b39e321e0db27dcde |
| core_runtime | k_atlas/browser/instagram_profile/Default/Code Cache/js/1e4759fe611aa0c9_0 | 13715 | f6165c3a9b029ca9198906078e2ab048f8753b6a7ad20c8c07e1faac9f37d25a |
| core_runtime | k_atlas/browser/instagram_profile/Default/Code Cache/js/22139631f133ba41_0 | 235 | a987a3ff3a5a5942e9d48f9971033ec089227bff06154916601f25098c761080 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Code Cache/js/222bc9f0def5f56d_0 | 6595 | b41783889f3650decc75228058879763f0af0dacaa2d2902ea078fd9e5d45f15 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Code Cache/js/2368332385a73f19_0 | 248 | cf8a44b5aa0a2ba5ba8f5a566c52a96b5b2fca727be8a29a5ed0b6108c1a943c |
| core_runtime | k_atlas/browser/instagram_profile/Default/Code Cache/js/296188074483d49f_0 | 235 | eccac3fd8e6b6612865451214280cfed4dbd07f2788231380d3aa655c3f7c7fb |
| core_runtime | k_atlas/browser/instagram_profile/Default/Code Cache/js/2aa28f82d85f9246_0 | 248 | e4ce9ca8a45ee5bfcac07c57efa30447fbb4bffc99b3bf3a705d74fa79fa3f0d |
| core_runtime | k_atlas/browser/instagram_profile/Default/Code Cache/js/2c8a80152d496e38_0 | 235 | 96f1ddaedf6e82a96a28528ccc7ea4feaf278a017b7735da9eb701d1c5f76223 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Code Cache/js/2f7ba27d81febaf4_0 | 246 | c64e113367ae4ce9001cce7816f30aa5006360809174ef6d8ba7b2bc11ed9f8d |
| core_runtime | k_atlas/browser/instagram_profile/Default/Code Cache/js/3302d043d8cbb8d7_0 | 243 | 0a1251fcb53db4a51f291715f5a7328d5b26322696cb46f3a5a0c3629207cf8a |
| core_runtime | k_atlas/browser/instagram_profile/Default/Code Cache/js/344475666ce7a065_0 | 23216 | 9ccd2c50dd32e45168fb13b20da8b687bf5258d599ed4146013074427b30617f |
| core_runtime | k_atlas/browser/instagram_profile/Default/Code Cache/js/345e1e5fcf0a0bfb_0 | 246 | b4efdf89ef6716252ce096fe5fb008eb2f9d9e1400f9a7445b4eebb6d80d06fc |
| core_runtime | k_atlas/browser/instagram_profile/Default/Code Cache/js/361acea471ee0d0b_0 | 235 | fe2550df93848d3bade5d428e79714d903f4af68a3ffa4155d7e3f4deba923be |
| core_runtime | k_atlas/browser/instagram_profile/Default/Code Cache/js/39465967047c282a_0 | 246 | 6e7938119b2c8a8950aedb288f6ea45e800bec1da0748dd1a16cc03923b2df71 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Code Cache/js/3e9ff17f9537ce99_0 | 1059 | 79cb48eabbd1aea904fc36f56d88947a9c3ba9c763d07938431cc3761cba1283 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Code Cache/js/401aa99866ea676a_0 | 235 | 6689ff256c2493b065d097c5a9c1e4ecf37126444ad89b16f0ddcc601609c494 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Code Cache/js/425f8ba538cc749a_0 | 235 | 72107112c18019244d50f809c9a0696012d92701aaa0c43128ecaaef9f29f8d6 |
| core_runtime | k_atlas/browser/instagram_profile/Default/Code Cache/js/42eb8611f04aa272_0 | 235 | d7dfe41fd676dfd7aa3cd2cfb1f02b854e16b2ae06a66ba2c9727899632d47d6 |

## Garantias de nao exportacao sensivel

- secret_export_performed: False
- local_secrets_export_performed: False
- memory_runtime_export_performed: False
- files_copied: False
- archive_created: False
- backup_restore_executed: False
- automatic_remediation_executed: False
- real_drill_executed: False
- real_recovery_executed: False
- real_rollback_executed: False
- git_reset_hard_executed: False
- force_push_executed: False
- destructive_shell_executed: False
- memory_deletion_executed: False

## Operacoes bloqueadas

- secret_export
- local_secrets_export
- memory_runtime_export
- backup_restore_execution
- real_drill_execution
- real_recovery_execution
- real_rollback_execution
- git_reset_hard
- force_push
- destructive_shell
- memory_deletion
- automatic_remediation

## Decisao operacional

Pacote de backup/export criado como manifesto seguro, sem copiar conteudo e sem criar arquivo compactado.
O sistema pode seguir para 084 - K-OS Release Candidate Gate Core.
