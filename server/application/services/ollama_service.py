import ollama
from ollama import Client
import base64
from server.application.exceptions.ollama import OllamaError

class ChatHistory:
    """
    Datastructure to store chat history
    """
    def __init__(self):
        self.history = []
        
    def add_history(self, user_message, assistant_message):
        """
        Add a new message to chat history
        :param user_message: the user's message
        :param assistant_message: the assistant's message
        """
        self.history.append(
            {
                "role": "user",
                "content": user_message
            }
        )
        self.history.append(
            {
                "role": "assistant",
                "content": assistant_message
            }
        )
    
    def get_history(self):
        """
        Get chat history
        :return: the list of chat history
        """
        return self.history

    def clear_history(self):
        """
        Clear chat history
        """
        self.history = []

class OllamaService:
    def __init__(self, host='http://localhost:11434'):
        """
        Initialize the Ollama service with the host of ollama server
        :param host: the host of ollama server
        :retrun: None
        """
        try:
            self.__client = Client(host = host)
            self.__chat_history = ChatHistory()
        except Exception as e:
            raise OllamaError(f"Failed to initialize OllamaService: {str(e)}")
    
    def get_model_list(self):
        """
        Get the list of models available on the ollama server
        :return: the list of model names
        """
        try:
            list_response = self.__client.list()
            model_list = []
            for i in list_response.models:
                model_list.append(i.model)
            return model_list
        except ollama.ResponseError as e:
            raise OllamaError(f"Failed to get model list, HTTP status code: {e.status_code}")
        except Exception as e:
            raise OllamaError(f"Failed to get model list: {str(e)}")
        
    def is_model_available(self, model_name):
        """
        Check if a model is available on the ollama server
        :param model_name: the name of the model
        :return: True if the model is available, False otherwise
        """
        if not model_name:
            raise OllamaError("Model name cannot be empty")
        # Try to get the list of model names
        try:
            model_list = self.get_model_list()
            return model_name in model_list
        except (OllamaError, Exception) as e:
            raise OllamaError(f"Failed to check if model is available: {str(e)}")

    def pull(self, model_name):
        """
        Pull a model from the ollama model library
        :param: model_name: name of the model to pull
        :return: True if the model is pulled successfully, False otherwise
        """
        if not model_name:
            raise OllamaError("Model name cannot be empty")
        # Try to pull the model
        try:
            # Check whether the model is already available
            try:
                if self.is_model_available(model_name):
                    return True
            except OllamaError as e:
                raise e
            # Pull the model
            try:
                ollama.pull(model_name)
                return True
            except ollama.ResponseError as e:
                raise e
        except ollama.ResponseError as e:
            raise OllamaError(f"Failed to pull model {model_name}, HTTP status code: {e.status_code}")
        except (OllamaError, Exception) as e:
            raise OllamaError(f"Failed to pull model {model_name}: {str(e)}")

    def __encode_image_to_base64(self, image_path):
        """
        Encode an image to base64
        :param image_path: the path to the image
        :return: the base64 encoded string
        """
        if not image_path:
            raise OllamaError("Image path cannot be empty")
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")
        except Exception as e:
            raise OllamaError(f"Failed to encode image to base64: {str(e)}")

    def chat(self, model_name, prompt, include_history = False, image_path = None):
        """
        Chat with the LLM
        :param: model_name: the name of the model/LLM
        :prompt: the message sent to the model/LLM
        :include_history: True if the chat history is included, False otherwise
        :image_path: the path of the image
        :return: the response message from the model/LLM
        """
        if not model_name:
            raise OllamaError("Model name cannot be empty")
        # Check whether the model is available
        if not self.is_model_available(model_name):
            raise OllamaError(f"Model {model_name} is not available")
        # Try to chat with the model/LLM
        try:
            messages = [
                {
                    "role": "system",
                    "content": '''
                    You are a knowledge agent, you will be given some instructions and tasks,
                    and your duty is to follow the instructions and complete the tasks.
                    For example, you may be given some notes and required to analyze the
                    relationship between the notes or summarize them.
                    '''
                }
            ]
            image_base64 = None
            if not image_path:
                if include_history:
                    history = self.__chat_history.get_history()
                    for i in history:
                        messages.append(i)
                messages.append(
                    {
                        "role": "user",
                        "content": prompt
                    }
                )
            else:
                # Encode the image to base64 and add it to the message
                
                
                try:
                    image_base64 = self.__encode_image_to_base64(image_path)
                    print(f"Image {image_path} transferred to base64")
                    messages.append(
                        {
                            "role": "user",
                            "content": f"An image has been sent hereby, please reply in according to the content of this image. {prompt}",
                            "image": [image_base64]
                        }
                    )
                except OllamaError as e:
                    raise e
            # Send the messages to the model/LLM
            response = self.__client.chat(model = model_name, messages = messages)
            # Add user prompt and model/LLM response to chat history
            if image_base64 is None:
                self.__chat_history.add_history(
                    user_message = prompt,
                    assistant_message = response.message.content
                )
            else:
                self.__chat_history.add_history(
                    user_message = f"{prompt} Image: {image_base64}",
                    assistant_message = response.message.content
                )
            return response.message.content
        except ollama.ResponseError as e:
            raise OllamaError(f"Failed to chat with the model/LLM, HTTP status code: {e.status_code}")
        except (OllamaError, Exception) as e:
            raise OllamaError(f"Failed to chat with the model/LLM: {str(e)}")

    def get_chat_history(self):
        """
        Get chat history
        :return: the chat history (list of directions)
        """
        try:
            return self.__chat_history.get_history()
        except Exception as e:
            raise OllamaError(f"Failed to get chat history: {str(e)}")

    def clear_chat_history(self):
        """
        Clear chat history
        :return: True if the chat history is cleared successfully, False otherwise
        """
        try:
            self.__chat_history.clear_history()
            return True
        except Exception as e:
            raise OllamaError(f"Failed to clear chat history: {str(e)}")