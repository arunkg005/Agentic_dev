FROM python:3.11

# Set up a new user named "user" with user ID 1000
# HuggingFace requires applications to run as a non-root user
RUN useradd -m -u 1000 user

# Switch to the "user" user
USER user

# Set home to the user's home directory
ENV HOME=/home/user \
	PATH=/home/user/.local/bin:$PATH

# Set the working directory to the user's home directory
WORKDIR $HOME/app

# Copy the current directory contents into the container at $HOME/app setting the owner to the user
COPY --chown=user . $HOME/app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create the output directory and ensure it is writable by the user
RUN mkdir -p output && chmod 777 output

# Expose port 7860 (required by HuggingFace Spaces)
EXPOSE 7860

# Command to run the application using uvicorn on port 7860
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
