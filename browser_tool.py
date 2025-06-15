# Browser Tool for LangEntiChain
"""
Selenium-based browser tool for web automation
Inspired by AgenticSeek's browser implementation
"""

import os
import time
import json
from typing import Dict, List, Optional, Any
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.keys import Keys
import tempfile


def create_browser_driver(headless: bool = True) -> webdriver.Chrome:
	"""Create a Chrome WebDriver instance"""
	chrome_options = Options()
	
	if headless:
		chrome_options.add_argument("--headless=new")
		chrome_options.add_argument("--disable-gpu")
	
	# Common options for stability
	chrome_options.add_argument("--no-sandbox")
	chrome_options.add_argument("--disable-dev-shm-usage")
	chrome_options.add_argument("--disable-blink-features=AutomationControlled")
	chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
	
	# Suppress Chrome warnings and errors
	chrome_options.add_argument("--log-level=3")  # Fatal errors only
	chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
	chrome_options.add_argument("--silent")
	
	# Disable images and CSS for faster loading (optional)
	prefs = {
		"profile.default_content_setting_values": {
			"notifications": 2  # Block notifications
		}
	}
	chrome_options.add_experimental_option("prefs", prefs)
	
	# Create temp profile
	user_data_dir = tempfile.mkdtemp(prefix="chrome_profile_")
	chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
	
	try:
		# Try to create driver (assumes ChromeDriver is in PATH)
		driver = webdriver.Chrome(options=chrome_options)
		return driver
	except Exception as e:
		print(f"Failed to create Chrome driver: {e}")
		print("Make sure ChromeDriver is installed and in your PATH")
		print("Download from: https://chromedriver.chromium.org/")
		raise


class BrowserTool:
	"""Browser automation tool using Selenium"""
	
	def __init__(self, driver: webdriver.Chrome):
		self.driver = driver
		self.wait = WebDriverWait(self.driver, 10)
		self.screenshot_dir = ".screenshots"
		os.makedirs(self.screenshot_dir, exist_ok=True)
	
	def navigate_to(self, url: str) -> str:
		"""Navigate to a URL"""
		try:
			if not url.startswith(('http://', 'https://')):
				url = 'https://' + url
			
			self.driver.get(url)
			time.sleep(2)  # Wait for page load
			
			return f"Successfully navigated to {url}. Page title: {self.driver.title}"
		except Exception as e:
			return f"Error navigating to {url}: {str(e)}"
	
	def get_page_text(self, limit: int = 5000) -> str:
		"""Extract text content from the current page"""
		try:
			# Get body text
			body = self.driver.find_element(By.TAG_NAME, "body")
			text = body.text
			
			# Limit text length
			if len(text) > limit:
				text = text[:limit] + "... (truncated)"
			
			return f"Page content:\n{text}"
		except Exception as e:
			return f"Error extracting text: {str(e)}"
	
	def fill_form(self, form_data: str) -> str:
		"""Fill form fields with provided data"""
		try:
			# Parse form data
			if isinstance(form_data, str):
				try:
					data = json.loads(form_data)
				except:
					# Try to parse simple format: "field1=value1, field2=value2"
					data = {}
					for pair in form_data.split(','):
						if '=' in pair:
							key, value = pair.strip().split('=', 1)
							data[key.strip()] = value.strip()
			else:
				data = form_data
			
			results = []
			for field_name, value in data.items():
				try:
					# Try different strategies to find the input
					element = None
					
					# Try by name
					try:
						element = self.driver.find_element(By.NAME, field_name)
					except:
						pass
					
					# Try by id
					if not element:
						try:
							element = self.driver.find_element(By.ID, field_name)
						except:
							pass
					
					# Try by placeholder
					if not element:
						try:
							element = self.driver.find_element(
								By.XPATH, f"//input[@placeholder='{field_name}']"
							)
						except:
							pass
					
					if element:
						element.clear()
						element.send_keys(value)
						results.append(f"Filled {field_name} with {value}")
					else:
						results.append(f"Could not find field: {field_name}")
						
				except Exception as e:
					results.append(f"Error filling {field_name}: {str(e)}")
			
			return "Form filling results:\n" + "\n".join(results)
			
		except Exception as e:
			return f"Error filling form: {str(e)}"
	
	def click_element(self, selector: str) -> str:
		"""Click an element by text or CSS selector"""
		try:
			element = None
			
			# Try to find by link text
			try:
				element = self.driver.find_element(By.LINK_TEXT, selector)
			except:
				pass
			
			# Try by partial link text
			if not element:
				try:
					element = self.driver.find_element(By.PARTIAL_LINK_TEXT, selector)
				except:
					pass
			
			# Try by button text
			if not element:
				try:
					element = self.driver.find_element(
						By.XPATH, f"//button[contains(text(), '{selector}')]"
					)
				except:
					pass
			
			# Try as CSS selector
			if not element:
				try:
					element = self.driver.find_element(By.CSS_SELECTOR, selector)
				except:
					pass
			
			if element:
				# Scroll to element
				self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
				time.sleep(0.5)
				
				# Click
				element.click()
				time.sleep(1)
				
				return f"Successfully clicked element: {selector}"
			else:
				return f"Could not find element: {selector}"
				
		except Exception as e:
			return f"Error clicking element: {str(e)}"
	
	def take_screenshot(self, filename: Optional[str] = None) -> str:
		"""Take a screenshot of the current page"""
		try:
			if not filename:
				filename = f"screenshot_{int(time.time())}.png"
			
			filepath = os.path.join(self.screenshot_dir, filename)
			self.driver.save_screenshot(filepath)
			
			return f"Screenshot saved to {filepath}"
		except Exception as e:
			return f"Error taking screenshot: {str(e)}"
	
	def get_links(self) -> str:
		"""Extract all links from the current page"""
		try:
			links = self.driver.find_elements(By.TAG_NAME, "a")
			link_data = []
			
			for link in links[:20]:  # Limit to first 20 links
				href = link.get_attribute("href")
				text = link.text.strip()
				if href and text:
					link_data.append(f"{text}: {href}")
			
			return "Links found:\n" + "\n".join(link_data)
		except Exception as e:
			return f"Error getting links: {str(e)}"
	
	def go_back(self) -> str:
		"""Go back to the previous page"""
		try:
			self.driver.back()
			time.sleep(1)
			return f"Went back. Current page: {self.driver.title}"
		except Exception as e:
			return f"Error going back: {str(e)}"
	
	def execute_javascript(self, script: str) -> str:
		"""Execute JavaScript on the page"""
		try:
			result = self.driver.execute_script(script)
			return f"JavaScript executed. Result: {result}"
		except Exception as e:
			return f"Error executing JavaScript: {str(e)}"
	
	def wait_for_element(self, selector: str, timeout: int = 10) -> str:
		"""Wait for an element to appear"""
		try:
			element = WebDriverWait(self.driver, timeout).until(
				EC.presence_of_element_located((By.CSS_SELECTOR, selector))
			)
			return f"Element {selector} is present"
		except TimeoutException:
			return f"Timeout waiting for element: {selector}"
		except Exception as e:
			return f"Error waiting for element: {str(e)}"
	
	def get_form_inputs(self) -> str:
		"""Get all form inputs on the page"""
		try:
			inputs = self.driver.find_elements(By.TAG_NAME, "input")
			textareas = self.driver.find_elements(By.TAG_NAME, "textarea")
			selects = self.driver.find_elements(By.TAG_NAME, "select")
			
			form_info = []
			
			for inp in inputs:
				input_type = inp.get_attribute("type") or "text"
				name = inp.get_attribute("name") or inp.get_attribute("id") or "unnamed"
				placeholder = inp.get_attribute("placeholder") or ""
				form_info.append(f"Input ({input_type}): {name} - {placeholder}")
			
			for textarea in textareas:
				name = textarea.get_attribute("name") or textarea.get_attribute("id") or "unnamed"
				form_info.append(f"Textarea: {name}")
			
			for select in selects:
				name = select.get_attribute("name") or select.get_attribute("id") or "unnamed"
				form_info.append(f"Select: {name}")
			
			return "Form fields found:\n" + "\n".join(form_info)
		except Exception as e:
			return f"Error getting form inputs: {str(e)}"
	
	def close(self):
		"""Close the browser"""
		try:
			self.driver.quit()
		except:
			pass


# Test the browser tool
if __name__ == "__main__":
	import configparser
	
	print("Testing Browser Tool...")
	
	# Load config
	config = configparser.ConfigParser()
	config.read('config.ini')
	headless = config.getboolean('BROWSER', 'headless', fallback=False)
	
	# Create browser
	driver = create_browser_driver(headless=headless)
	browser = BrowserTool(driver)
	
	try:
		# Test navigation
		print(browser.navigate_to("https://www.example.com"))
		print(browser.get_page_text())
		
		# Wait before closing
		input("Press Enter to close browser...")
		
	finally:
		browser.close()
