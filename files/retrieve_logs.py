    def get_all_events(self, index_name):
        """Retrieve all the events, and filter them for detecting CPU overload"""
        es = Elasticsearch()
        all_cpu_utilization = es.search(index=index_name, body={"query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "agent.type": "metricbeat"
                        }
                    },
                    {
                        "match": {
                            "service.type": "system"
                        }
                    },
                    {
                        "match": {
                            "event.dataset": "system.cpu"
                        }
                    }
                ]
            }
        }
        }, size=10000)

        all_applicative_logs = es.search(index=index_name, body={"query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "agent.type": "filebeat"
                        }
                    }
                ]
            }
        }
        }, size=10000)

        # Read all log_message
        for i in range(all_applicative_logs['hits']['total']['value']):
            if "_grokparsefailure" not in all_applicative_logs['hits']['hits'][i]['_source']['tags']:
                self.logs.add(all_applicative_logs['hits']['hits'][i]['_source']['log_message'])

        # For each CPU Utilization data, store the applicative logs who arrived in the last 20 minutes
        for i in range(all_cpu_utilization['hits']['total']['value']):
            last_applicative_logs = es.search(index=index_name, body={"query": {
                "bool": {
                    "must": [
                        {
                            "match": {
                                "agent.type": "filebeat"
                            }
                        },
                        {
                            "range": {
                                "@timestamp": {
                                    "gte": all_cpu_utilization['hits']['hits'][i]['_source']['@timestamp'][
                                           :-1] + "||-20m",
                                    "lt": all_cpu_utilization['hits']['hits'][i]['_source']['@timestamp'][:-1]
                                }
                            }
                        }
                    ]
                }
            }
            })

            self.transactions[i] = dict.fromkeys(self.logs, 0)

            if all_cpu_utilization['hits']['hits'][i]['_source']['system']['cpu']['total']['pct'] > 2.0:
                self.transactions[i]["CPU Overload"] = 1
            else:
                self.transactions[i]["Nominal CPU utilization"] = 1

            for j in self.logs:
                log_is_present = False
                for k in last_applicative_logs['hits']['hits']:
                    if "_grokparsefailure" not in k['_source']['tags'] and k['_source']['log_message'] == j:
                        log_is_present = True
                        break

                self.transactions[i][j] = 1 if log_is_present else 0
