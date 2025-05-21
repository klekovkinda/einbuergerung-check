from llama_cpp import Llama

def build_html_message_with_llm(start_at: str = "00:00:00", finish_at: str = "00:00:00", execution_times: int = 0,
                                successful_notifications: int = 0, available_dates: int = 0, failed_requests: int = 0,
                                new_users: int = 0, missing_users: int = 0)->str:
    prompt = ("Bot statistics for the specified time period. "
              f"Time from {start_at} to {finish_at}, "
              f"Number of requests: {execution_times}, "
              f"Number of notifications sent: {successful_notifications}, "
              f"Number of available dates: {available_dates}, "
              f"Number of failed requests: {failed_requests}, "
              f"Number of new users: {new_users}, "
              f"Number of users who left the channel: {missing_users}. "
              f"Generate a text message for the channel, present these statistics in a friendly and informative way for users. In English. "
              f"In the message I also expect to see the time when the bot was sending the messages."
              )
    llm = Llama(model_path="../phi-2.Q4_K_M.gguf", n_ctx=1024, n_threads=4)
    output = llm(prompt, max_tokens=256)
    message = output["choices"][0]["text"].strip()
    return message

print(build_html_message_with_llm(start_at="00:06:00", finish_at="23:59:59", execution_times=506, successful_notifications=23, available_dates=5, failed_requests=2, new_users=3, missing_users=1))
